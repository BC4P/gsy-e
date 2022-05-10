The Matching API is responsible for communicating with a running local simulation of the Grid Singularity Exchange. The client uses the Matching API to dynamically connect to the simulated electrical grid and query the open bids/offers and post-trading recommendations back to Grid Singularity Exchange.

###request_offers_bids()

This command is used to request bids and offers from a specific market or family of markets, that can be specified through the **filters** dictionary and it is the output of the on_area_map_response method above explained.
```
self.request_offers_bids(filters={“markets: self.id_list})
```
