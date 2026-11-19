# Map data

`cities.csv` lists 105 European cities connected by road. `roads.csv` lists 262 roads between them.

Road distances are driving kilometres obtained on 4 November 2026 from the public OSRM routing service, which runs on OpenStreetMap data. Map data © OpenStreetMap contributors, available under the Open Database Licence (ODbL).

How the roads were chosen:

1. Each city was paired with its 6 nearest cities.
2. Routes that use a ferry or train were removed. All roads are driven.
3. Routes longer than 1.9 times the straight line were removed, because they mean going around a sea or a mountain range.
4. A road was removed when going through a third city is at most 5% longer, because that road essentially runs through that city. Removals never disconnect the map.

Each distance is one direction of travel, rounded up to the next kilometre and used in both directions. The match never queries any routing service. Everything is in these files.
