Grid Singularity energy exchange engine (D3A) organizes the grid into **hierarchical markets**. For example, household assets are initially grouped into a household market, which are in turn grouped into higher-level markets such as neighborhoods, districts, or regions. Since the grid is already organized by different voltage levels, the hierarchies of markets in the D3A can **reflect the different voltage levels** of the grid. This allows [grid fees](grid-fees.md) to be accounted for in each [market](model-markets.md). This type of structure enables grid operators to source flexibility for targeted **congestion management** or **frequency balancing**. It also facilitates easy scaling by connecting diverse energy communities.

Market participants such as energy assets are represented by **agents**, trading algorithms defined by user-set parameters, which act like **traders**. Energy prices are established by **bids** and **offers** and are issued by agents according to the [trading strategies](default-trading-strategy.md) of market participants. 

Energy assets trade with each other and with other submarkets inside a parent market. In this way energy trading can be organized into groups or communities by registering assets in the relevant markets. These markets are then stacked in a **market hierarchy** to allow inter-market trading across the entire grid infrastructure, while prioritizing trade in the local markets. The utility is also represented by an agent, the [Market Maker](model-market-maker.md).

Trading happens at the most cost-efficient level following a select [market mechanism](clearing-purpose.md). This will typically be locally, but if an actor (e.g., a grid operator) has set certain parameters that place a better bid into the market due to a high need (e.g. for grid flexibility), [inter-area trading agents](inter-area-agent.md) can match it with offers from a lower or higher-level market. Grid operators may also levy flexible grid fees on local markets to help manage congestion.

It is important to note that the D3A is not, itself, trading energy or providing balancing services. Rather, it is creating the **exchange**, registering assets, and providing the mechanism of agents to allow assets and markets to place bids and offers and trade directly with one another (i.e., peer-to-peer) in a fully decentralized manner, or, if there is insufficient local generation, from the  utility. This decentralized structure removes limits to scaling.  If the D3A is deployed to facilitate a local distributed energy exchange, the traditional roles of the grid operator, which manages the connection to the power grid, and the utility, as a provider of energy, would continue to be required to integrate the local energy market with the wider grid network.** **The primary difference is that a utility would no longer be the only market actor with which a household exchanges energy, but one of multiple.

Grid Singularity’s D3A is a highly innovative and effective grid modernization solution. 


1. First, it creates a **resilient market** by ensuring equal access, transparent pricing, and trading at optimal market levels (i.e., between assets and buildings or facility and grid). 
2. Second, it **incentivizes and facilitates** the integration of clean DERs onto the grid closer to load centers. 
3. Third, grid operators can use it to **implement flexible grid tariffs** to benefit from the local market flexibility to alleviate congestion. 
4. Fourth, the [Grid Singularity API](api-overview.md) provides instantaneous granular data to the grid operator–which historically has relied upon changes in detected load and alterations from the forecast–enabling the operator to improve management, flexibility, and grid performance. 
5. Fifth, peer-to-peer trading is **market-driven**, not based upon predetermined pricing, which optimizes local consumption and thus the use of (cheaper) local renewables, increasing affordability, reducing reliance and overall/peak load on the grid, supporting efficient asset utilization, and reducing system losses. 
6. Sixth, it **increases community self-sufficiency and energy savings**, providing emergency power backup, and mitigating the need for new transmission infrastructure. Seventh, the software empowers customer engagement in energy markets by lowering barriers, creating cost incentives, and increasing choice (e.g., type of energy consumed or preferred trading partner). 
7. Finally, the peer-to-peer trading system **incentivizes private investment** in electric system infrastructure by increasing revenue from renewable DERs and providing decision-making tools.

Grid Singularity fosters **interoperability** and **open-source** development, **collaborating** with other market actors that provide grid management and asset aggregation services. Our software is **agnostic to regulation**, with regulatory compliance such as balance reporting provided by implementation partners.