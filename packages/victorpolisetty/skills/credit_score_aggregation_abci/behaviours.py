# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2024 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This package contains round behaviours of CreditScoreAggregationAbciApp."""

from abc import ABC
from typing import Generator, Set, Type, cast

from packages.valory.skills.abstract_round_abci.base import AbstractRound
from packages.valory.skills.abstract_round_abci.behaviours import (
    AbstractRoundBehaviour,
    BaseBehaviour,
)
from packages.victorpolisetty.skills.credit_score_aggregation_abci.models import Params, SharedState
from packages.victorpolisetty.skills.credit_score_aggregation_abci.payloads import (
    HelloPayload,
    CollectTalentProtocolScorePayload,
)
from packages.victorpolisetty.skills.credit_score_aggregation_abci.rounds import (
    CreditScoreAggregationAbciApp,
    HelloRound,
    CollectTalentProtocolScoreRound,
    SynchronizedData,
)


class HelloBaseBehaviour(BaseBehaviour, ABC):  # pylint: disable=too-many-ancestors
    """Base behaviour for the hello_abci skill."""

    @property
    def synchronized_data(self) -> SynchronizedData:
        """Return the synchronized data."""
        return cast(SynchronizedData, super().synchronized_data)

    @property
    def params(self) -> Params:
        """Return the params."""
        return cast(Params, super().params)

    @property
    def local_state(self) -> SharedState:
        """Return the state."""
        return cast(SharedState, self.context.state)


class HelloBehaviour(HelloBaseBehaviour):  # pylint: disable=too-many-ancestors
    """HelloBehaviour"""

    matching_round: Type[AbstractRound] = HelloRound

    def async_act(self) -> Generator:
        """Do the act, supporting asynchronous execution."""

        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            sender = self.context.agent_address
            payload_content = "Hello world!"
            self.context.logger.info(payload_content)
            payload = HelloPayload(sender=sender, content=payload_content)

        with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
            yield from self.send_a2a_transaction(payload)
            yield from self.wait_until_round_end()

        self.set_done()

class CollectTalentProtocolScoreBehaviour(HelloBaseBehaviour):  # pylint: disable=too-many-ancestors
    """Behaviour to observe and collect Talent Protocol score."""

    matching_round = CollectTalentProtocolScoreRound

    def async_act(self) -> Generator:
        """
        Do the action.

        Steps:
        - Ask the configured API for historical stock price data.
        - If the request fails, retry until max retries are exceeded.
        - Send an observation transaction and wait for it to be mined.
        - Wait until ABCI application transitions to the next round.
        - Go to the next behaviour (set done event).
        """

        # Check if maximum retries have been exceeded
        if self.context.talent_protocol_score_response.is_retries_exceeded():
            # Wait to see if other agents can progress the round, otherwise restart
            with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
                yield from self.wait_until_round_end()
            self.set_done()
            return

        # Measure the local execution time of the HTTP request
        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            # Prepare API request specifications
            api_specs = self.context.talent_protocol_score_response.get_spec()

            # Make the asynchronous HTTP request to the Talent Protocol API
            response = yield from self.get_http_response(
                method=api_specs["method"],
                url=api_specs["url"],
                headers=api_specs["headers"],
                parameters=api_specs["parameters"],
            )

        try:
            talent_protocol_response = self.context.talent_protocol_score_response.process_response(response)
        except Exception as e:
            self.context.logger.error(f"Error processing Talent Protocol response: {e}")
            talent_protocol_response = None

        # Extract the 'score' value safely
        if talent_protocol_response:
            talent_protocol_score = str(talent_protocol_response.get("passport", {}).get("score", ""))
        else:
            talent_protocol_score = ""

        # Handle the API response
        if talent_protocol_score:
            self.context.logger.info(
                f"Got talent_protocol_score from {self.context.talent_protocol_score_response.api_id}: {talent_protocol_score}"
            )
            payload = CollectTalentProtocolScorePayload(
                self.context.agent_address, talent_protocol_score
            )

            # Send a transaction and wait for the round to end
            with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
                yield from self.send_a2a_transaction(payload)
                yield from self.wait_until_round_end()
            self.set_done()
        else:
            self.context.logger.warning(
                f"Could not retrieve a valid talent_protocol_score from {self.context.talent_protocol_score_response.api_id}"
            )

            # Wait before retrying
            yield from self.sleep(
                self.context.talent_protocol_score_response.retries_info.suggested_sleep_time
            )
            self.context.talent_protocol_score_response.increment_retries()


class CreditScoreAggregationRoundBehaviour(AbstractRoundBehaviour):
    """CreditScoreAggregationBehaviour"""

    initial_behaviour_cls = HelloBehaviour
    abci_app_cls = CreditScoreAggregationAbciApp  # type: ignore
    behaviours: Set[Type[BaseBehaviour]] = [  # type: ignore
        HelloBehaviour,
        CollectTalentProtocolScoreBehaviour
    ]