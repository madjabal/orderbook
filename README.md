# Order Book Package

## Overview
This provides a limit order book written in Python that supports two kinds of orders:
- Limit
- Market
The book has price/time priority, meaning orders are matched at the best price and the oldest order for a given price.

## Strengths
This package provides for efficient handling of orders that occur in several edge cases:
- Maket order submitted with no opposing limit
  - The OrderBook keeps track of outstanding market orders in a MarketOrderQueue
  - Executes them with time priority when matching limits appear
- Limit order that crosses spread
  - Treated as a market order with a price constraint
  - Executes at levels better than the limit price
    - Saves a limit order if there is remaining quantity

## Weaknesses
This package focused on expediency and has a lack of tests as a result. The main tests are for 2 components
- Order Creation
- OrderBook operations

In this way we have minimum coverage to have high confidence in the program: the order creation package is used by  
users to create orders and sets expectations for downstream code, so it must be tested. The OrderBook has complicated  
logic and its tests serves as end-to-end for underlying components

## Implementation
Implementation follows from efficiency considerations. Two top level operations were desired to be as quick as possible:
- Add Order
  - (O(log(n)) for first limit order at a price, where n is number of prices in that side of the book)
  - (O(c) otherwise and for market orders)
- Cancel Order
  - (O(log(n)) for last limit order at a price, where n is number of prices in that side of the book)
  - (O(c) otherwise and for market orders)

This was done for each side of the limit order book using:
- sorted list for prices
- map from price to DoublyLinkedList of orders
- map from order ID to DoublyLinkedList node for the order

And for each side of the market order queues:
- DoublyLinkedList of orders
- map from order ID to DoublyLinkedList node for the order

Using DoublyLinkedLists with mapped references allows us to remove from and add to those objects in constant time.  
The sorted price list is the main source of O(log(n)) operation time.

Matching and execution occurs when new orders are added:
- Non-crossing limit
  - No trade
- Crossing limit
  - At least one trade, possibly more
  - Possible new limit order if order not filled at limit price or better
- Market Order
  - At least one trade, possibly more 
  - Possible new MarketOrderQueue entry if not filled fully

Trades that result from these checks and matches are output with the best bid and best ask after execution.

Price and time priority is respected by processing a single order at a time and appending to ends of lists where time  
is appropriate and sorting by price where appropriate. For the case of the two MarketOrderQueue's we check order IDs  
(conveniently sequence numbers for easy time prioritization) at the top of each, since they were added in time order  
we are simply merging 2 sorted lists so the top order ID comparison is all that is needed.

### Concurrency Considerations
Concurrency is tricky within this framework. Some paths to consider:
- If a limit order is non-crossing, we can modify the opposite side of the book with another non-crossing limit order
- Market orders (from a new order or from the MarketOrderQueue) interact with only one side of the book, so we can allow the same kind of order to trade on the other side of the book
  - This preserves book state but trade order is no longer guaranteed
- Limit orders that cross may interact with both sides of the book
  - Larger reworks of how order IDs are checked is needed to make this a possibility

Overall this current implementation does not need to check order of trades unless flushing MarketOrderQueue's, a   
concurrent implementation would have to lean heavily on these in order to compensate for lost ordering guarantees.

## Performance
On a newer Mac laptop and running `demo.py` with a million orders takes under 2 seconds, taking around 2 microseconds  
per order (no cancels, only adds).

# Setup
This was developed using Python `3.12` with a simple requirements file of Pytest.

# Tests
Tests can be run (with the appropriate Python path) from root with:
```commandline
pytest test/
```

# Running
The `demo.py` script can be run directly, and has internal parameters to vary testing. It can be run by:
```commandline
python demo.py
```
It does not need the Pytest dependency.

# Further Development
Further development should use packages iSort and Black to maintain code formatting and style.
The next objectives for development should be:
- Better handling of order IDs (such as returning IDs to users)
- Deciding on an output for trade and best bid/ask data
- More rigorous tests, especially of underlying components
- Simplifying of logic in the order book
- Performance profiling and optimizations 