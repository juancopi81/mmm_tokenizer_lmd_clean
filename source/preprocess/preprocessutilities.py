# Original License:
# Copyright 2021 Tristan Behrens.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
from music21 import stream


def events_to_events_data(events):
    # Ensure right order. Float to deal with music21 Fractions
    events = sorted(events, key=lambda event: float(event[2]))

    events_data = []
    for event_index, event, event_next in zip(
        range(len(events)), events, events[1:] + [None]
    ):
        # event_index  event                    event_next
        # 0            ('NOTE_ON', 67, 0.0)     ('NOTE_OFF', 67, 4.0)
        # 1            ('NOTE_OFF', 67, 4.0)    None
        if event_index == 0 and event[2] != 0.0:
            event_data = {"type": "TIME_DELTA", "delta": float(event[2])}
            events_data += [event_data]

        event_data = {"type": event[0], "pitch": event[1]}
        events_data += [event_data]

        if event_next is None:
            continue

        delta = event_next[2] - event[2]
        assert delta >= 0, events
        if delta != 0.0:
            event_data = {"type": "TIME_DELTA", "delta": float(delta)}
            events_data += [event_data]

    # events_data
    # {'events': [{'type': 'NOTE_ON', 'pitch': 67}, {'type': 'TIME_DELTA', 'delta': 4.0},
    # {'type': 'NOTE_OFF', 'pitch': 67}]}, {'events': [{'type': 'NOTE_ON', 'pitch': 67},
    # {'type': 'TIME_DELTA', 'delta': 8.0}

    return events_data


def keep_first_eight_measures(score: stream.Score) -> stream.Score:
    # Create a new score for the output
    new_score = score.measures(1, 8)
    return new_score
