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

"""This package contains round behaviours of IdrissTokenFinderAggregationAbciApp."""

from abc import ABC
from typing import Generator, Set, Type, cast

from packages.valory.skills.abstract_round_abci.base import AbstractRound
from packages.valory.skills.abstract_round_abci.behaviours import (
    AbstractRoundBehaviour,
    BaseBehaviour,
)
from packages.victorpolisetty.skills.idriss_token_finder_aggregation_abci.models import Params, SharedState
from packages.victorpolisetty.skills.idriss_token_finder_aggregation_abci.payloads import (
    HelloPayload,
    CollectFarcasterSearchPayload,
)
from packages.victorpolisetty.skills.idriss_token_finder_aggregation_abci.rounds import (
    IdrissTokenFinderAggregationAbciApp,
    HelloRound,
    CollectFarcasterSearchRound,
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

class CollectFarcasterSearchBehaviour(HelloBaseBehaviour):  # pylint: disable=too-many-ancestors
    """Behaviour to observe and collect Farcaster Search."""

    matching_round = CollectFarcasterSearchRound

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
        if self.context.farcaster_search_response.is_retries_exceeded():
            # Wait to see if other agents can progress the round, otherwise restart
            with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
                yield from self.wait_until_round_end()
            self.set_done()
            return

        # Measure the local execution time of the HTTP request
        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            # Prepare API request specifications
            api_specs = self.context.farcaster_search_response.get_spec()

            # Make the asynchronous HTTP request to the Farcaster Search API
            response = yield from self.get_http_response(
                method=api_specs["method"],
                url=api_specs["url"],
                headers=api_specs["headers"],
                parameters=api_specs["parameters"],
            )

        try:
            farcaster_search_response = self.context.farcaster_search_response.process_response(response)
        except Exception as e:
            self.context.logger.error(f"Error processing Farcaster Search response: {e}")
            farcaster_search_response = None

        # Extract the response from farcaster search response
        if farcaster_search_response:
            farcaster_search_result = str(farcaster_search_response['casts'][0]['body']['data']['text'])
        else:
            farcaster_search_result = ""

        # Handle the API response
        # TODO: Fix here
        if farcaster_search_result:
            self.context.logger.info(
                f"Got farcaster_search_result from {self.context.farcaster_search_response.api_id}: {farcaster_search_result}"
            )
            payload = CollectFarcasterSearchPayload(
                self.context.agent_address, farcaster_search_result
            )

            # Send a transaction and wait for the round to end
            with self.context.benchmark_tool.measure(self.behaviour_id).consensus():
                yield from self.send_a2a_transaction(payload)
                yield from self.wait_until_round_end()
            self.set_done()
        else:
            self.context.logger.warning(
                f"Could not retrieve a valid farcaster_search_result from {self.context.farcaster_search_response.api_id}"
            )

            # Wait before retrying
            yield from self.sleep(
                self.context.farcaster_search_response.retries_info.suggested_sleep_time
            )
            self.context.farcaster_search_response.increment_retries()


class IdrissTokenFinderAggregationRoundBehaviour(AbstractRoundBehaviour):
    """IdrissTokenFinderAggregationBehaviour"""

    initial_behaviour_cls = HelloBehaviour
    abci_app_cls = IdrissTokenFinderAggregationAbciApp  # type: ignore
    behaviours: Set[Type[BaseBehaviour]] = [  # type: ignore
        HelloBehaviour,
        CollectFarcasterSearchBehaviour
    ]