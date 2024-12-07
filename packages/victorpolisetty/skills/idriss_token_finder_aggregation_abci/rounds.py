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

"""This package contains the rounds of IdrissTokenFinderAggregationAbciApp."""

from enum import Enum
from typing import Dict, FrozenSet, Optional, Set

from packages.victorpolisetty.skills.idriss_token_finder_aggregation_abci.payloads import (
    HelloPayload,
    CollectFarcasterSearchPayload
)
from packages.valory.skills.abstract_round_abci.base import (
    AbciApp,
    AbciAppTransitionFunction,
    AppState,
    BaseSynchronizedData,
    CollectSameUntilThresholdRound,
    CollectionRound,
    DegenerateRound,
    DeserializedCollection,
    EventToTimeout,
    get_name,
)


class Event(Enum):
    """IdrissTokenFinderAggregationAbciApp Events"""

    DONE = "done"
    NO_MAJORITY = "no_majority"
    ROUND_TIMEOUT = "round_timeout"


class SynchronizedData(BaseSynchronizedData):
    """
    Class to represent the synchronized data.

    This data is replicated by the tendermint application.
    """

    def _get_deserialized(self, key: str) -> DeserializedCollection:
        """Strictly get a collection and return it deserialized."""
        serialized = self.db.get_strict(key)
        return CollectionRound.deserialize_collection(serialized)

    @property
    def hello_data(self) -> Optional[str]:
        """Get the hello_data."""
        return self.db.get("hello_data", None)

    @property
    def participant_to_hello_round(self) -> DeserializedCollection:
        """Get the participants to the hello round."""
        return self._get_deserialized("participant_to_hello_round")

    @property
    def search_farcaster_search(self) -> Optional[str]:
        """Get the hello_data."""
        return self.db.get("hello_data", None)

    @property
    def participant_to_farcaster_search_round(self) -> DeserializedCollection:
        """Get the participants to the hello round."""
        return self._get_deserialized("participant_to_hello_round")


class HelloRound(CollectSameUntilThresholdRound):
    """HelloRound"""

    payload_class = HelloPayload
    synchronized_data_class = SynchronizedData
    done_event = Event.DONE
    no_majority_event = Event.NO_MAJORITY
    collection_key = get_name(SynchronizedData.participant_to_hello_round)
    selection_key = get_name(SynchronizedData.hello_data)

    # Event.ROUND_TIMEOUT  # this needs to be mentioned for static checkers


class CollectFarcasterSearchRound(CollectSameUntilThresholdRound):
    """CollectFarcasterSearchRound"""

    payload_class = CollectFarcasterSearchPayload
    synchronized_data_class = SynchronizedData
    done_event = Event.DONE
    no_majority_event = Event.NO_MAJORITY
    collection_key = get_name(SynchronizedData.search_farcaster_search)
    selection_key = get_name(SynchronizedData.participant_to_farcaster_search_round)


class FinishedHelloRound(DegenerateRound):
    """FinishedHelloRound"""


class IdrissTokenFinderAggregationAbciApp(AbciApp[Event]):
    """IdrissTokenFinderAggregationAbciApp"""

    initial_round_cls: AppState = HelloRound
    initial_states: Set[AppState] = {
        HelloRound,
    }
    transition_function: AbciAppTransitionFunction = {
        HelloRound: {
            Event.NO_MAJORITY: HelloRound,
            Event.ROUND_TIMEOUT: HelloRound,
            Event.DONE: CollectFarcasterSearchRound,
        },
        CollectFarcasterSearchRound: {
            Event.NO_MAJORITY: CollectFarcasterSearchRound,
            Event.ROUND_TIMEOUT: CollectFarcasterSearchRound,
            Event.DONE: FinishedHelloRound,
        },
        FinishedHelloRound: {},
    }
    final_states: Set[AppState] = {
        FinishedHelloRound,
    }
    event_to_timeout: EventToTimeout = {}
    cross_period_persisted_keys: FrozenSet[str] = frozenset()
    db_pre_conditions: Dict[AppState, Set[str]] = {
        HelloRound: set(),
    }
    db_post_conditions: Dict[AppState, Set[str]] = {
        FinishedHelloRound: set(),
    }