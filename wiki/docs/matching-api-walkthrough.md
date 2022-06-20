The Grid Singularity Matching Application Programming Interface (or Matching API) allows custom matching algorithms to be used to clear orders in local energy exchanges. The Matching API decouples the matching process from the exchange, allowing external algorithm providers (also termed mycos here) to read the exchange’s order book, run custom matching algorithms and send the resulting energy transactions to be verified and executed by the exchange, as shown in Figure 4 and explained below.

![alt_text](img/matching_api.png)

**Figure 4**. *Flow diagram of the role of mycos (third party matching algorithm providers) in the Grid Singularity Exchange.*

Trading process through the Matching API:

1. **Bids and Offers creation** - [Bids and Offers](market-agent.md) are created on behalf of the [energy assets](configuration.md) (either by using the [default GSy trading strategy](default-trading-strategy.md) or through the [Asset API](configure-trading-strategies-walkthrough.md)) and sent to the exchange.

2. **Order book** - The exchange gathers the bids and offers for all the different markets, which are currently organized in a [hierarchical structure](market-agent.md).

3. **Request Bids and Offers** - The Matching API requests bids and offers for [specific markets](matching-api-commands.md), and receives a dictionary containing all bids and offers posted in the chosen markets.

4. **Matching** - The Matching API pairs bids and offers together according to an external matching algorithm provided by a third-party matching algorithm provider and sends the proposed bid/offer pairs (technically called *recommendations*)  back to the exchange.

5. **Verification function** - Each recommendation is submitted to  the exchange’s verification function, a mechanism that checks whether the [clearing rate](two-sided-pay-as-clear.md) and the energy to be traded proposed by the recommendation respect the bids and offers’ [attributes and requirements](degrees-of-freedom.md).

6. **Transactions and rejections** - Recommended matches that pass the verification function’s check will be submitted as transactions in the Grid Singularity exchange. Recommendations rejected by the verification function will trigger a notification through the Matching API and not be sent to the exchange for clearing.

It is important to note that the Matching API is **asynchronous** towards the exchange, meaning  that [it can request bids and offers](matching-api-commands.md) and send recommendations at any time during the [market slots]('market-types.md').

To decouple the bids / offers matching mechanism from the exchange and to develop your customised clearing algorithm, please follow the following steps:

- Install the [Grid Singularity Myco SDK](https://github.com/gridsingularity/gsy-myco-sdk) on your computer by launching the following commands on your terminal window:

**Install gsy-e-sdk**

```
mkvirtualenv gsy-myco-sdk
pip install https://github.com/gridsingularity/gsy-myco-sdk.git
```
**Update gsy-myco-sdk (needed when an update is deployed)**
```
pip uninstall -y gsy-myco-sdk
pip install git+https://github.com/gridsingularity/gsy-myco-sdk.git
```
- Edit the [Matching API template script](matching-api-template-script.md) to connect with your customised matching algorithm.
- [Launch the Matching API script](registration-matching-api-user-interface.md) in a local (backend) simulation.

*Currently, it is not possible to connect the Matching API through a Collaboration / Canary Network.*