# Annotation for Relationship Extractions

This annotation tool was designed to be fed into input of [rel_component](https://github.com/explosion/projects/tree/v3/tutorials/rel_component), an **Entity Relation Extractions** tutorial project by [Explosion.ai](https://explosion.ai), maintainer of [spaCy](https://spacy.io). 

As that projects uses input `jsonl` file annotated with `Prodigy` (Advanced annotation tool also by [Explosion.ai](https://explosion.ai])), this tool aims to imitate that annotation process (Unlike, `Prodigy`, no annotation suggestions are provided).

But, to minimize the cumbersome process, this tool already prepopulated each **texts**, **tokens** and **entities**. While *relations* fields were already filled in, values are set to default, namely, `No-rel` (*No relations*).
With the following predefined relations, this tool helps to simplify the relations annotation process.

### Category Definitions (w/o Directions)

Consulting several papers, the following is a proposed categorization of relations between entities. (The example sentences below are not always based on the facts.)

- **Investment**: Buy, Sell, IPO, Privatization, Invest, Poach, Bid
    - `Buy` - **Microsoft** agreed to buy stakes in **Activision**. (- / +)
    - `Sell` - **Twitter** announced to sell its large share. (+ / +)
    - `IPO` - **Airbnb** debuted the **NYSE** amid investors’ surging interests. (+ / 0)
    - `Privatize` - **Nvidia** announced its sale of 10% stakes to **Softbank Japan**.
    - `Invest` - **Meta Platforms** invested a large portion of its capital into **metaverse**.
    - `Poach` - **Microsoft** poached bunch of C-suites from its rival **Google**.
    - `Bid` -
        - **Amazon** lost its bid for the DoD’s cloud project to **Microsoft**.
        - **Oracle** won the bid to become to become the supplier for the DoD’s DARPA project.
- **Cooperation**: Win-win situations (in-tandem)
- **Family / Ownership**: Same line of business (e.g., Franchise)
- **Performance**: Stock market performance
    - `Outperform` - **Microsoft** outperformed the **market** after it released the upbeat Q1 report. (+ / +)
    - `Underperform` - **Apple** trailed its **peers** while the tech index snapped the three-day losing streak. (- / +)
    - `In line` - As with its **peers**, **Nvidia** rallied premarket Monday. (+ / +)
- **Legal**: File, [Sued / Indicted / Subpoenaed / Alleged] (by), Win, Lose  (***Bidirectional***)
    
    <aside>
    💡 Replacement of verbs might be required (**Direction**)
    
    </aside>
    
    - `File` - **Google** filed a lawsuit against **Microsoft**. (+ / -)
    - `Indicted` - **Facebook** executives including Mark Zuckerberg were indicted on charges linked to Cambridge Analytica Scandal **by the DOJ**. (- / 0)
    - `Subpoenaed` - **Senate committee** yesterday issued a subpoena of top executives of social media companies including **Facebook** and **Twitter** related to the Jan 6 Capitol Hill insurrection. (0 / [-, -])
    - `Alleged` - **Microsoft** was alleged **by Google** of having obtained private information of Android OS.
    - `Win`
        - Yesterday, **Microsoft** won the high-stake suit against **Google**.
        - Yesterday, federal court in Sacramento concluded that **Microsoft** did not infringe the right of **Google**.
        - Yesterday, jury rule in favor of **Microsoft** against **Google**.
    - `Lose`
        - On Monday, **Apple** lost its bid to overturn the lawsuit **by Google**.
        - On Monday, **Apple** lost the high-stake suit **by Google**.
        - On Monday, judge ruled out that **Apple** violated **Google**’s copyright.
- **News release**: Launch, Patent, ***Authorization***
    - `Launch` -
        - **Apple** released newer handset of **iPhone** on Monday. (+ / +)
        - **Apple** launched **Apple Card** in Canada Monday. (+ / +)
    - `Patent` - **Apple** filed a patent for **magSafe**, a charging connector for its laptop computers.
    - `Authorize` -
        - **Pfizer** said that during the latest clinical trial, its **vaccine** was proven effective against the virus.
        - **Pfizer** said that during the latest clinical trial, its **vaccine** failed to show meaningful effects against the virus.
        - It was told that **FDA** revoked the recommendation of **J&J**’s one-shot COVID-19 vaccine.
        - **AstraZeneca** released that its **vaccine** won the approval of the Canadian Health authority.
- **Bankruptcy**: Entered, Exited
    - **Motorola** filed the bankruptcy Monday.
    - **Enron** went bankrupt after its ballooning debt went out of control.
    - **Qualcomm** exited its bankruptcy last month.


### Directions encoding

In view of sentiment analyses, directions between each entity is empirical. For the purpose, it makes sense to simplify by only(?) having three labels for the direction. (i.e., **over**, **under**, **[*pos/neg*]-inline**)

- `Over` - **A** verb **B** (A: positive, B: negative)
- `Under` - **A** verb **B** (A: negative, B: positive)
- `Posline` - **A** verb **B** (A: positive, B: positive)
- `Negline` - **A** verb **B** (A: negative, B: negative)
- `Pos` - **A** verb *(B)* (A: positive, B: neutral)
- `Neg` - **A** verb *(B)* (A: negative, B: neutral)


### Relations format

Combining both directions and categories, relations are formed as the following format.

`Direction`-`Category`

For instance, in the first sentence (**Microsoft** agreed to buy stakes in **Activision**.), the relation between `Microsoft`-`Activision` is `Under`-`Buy`.

It is because Microsoft is given inferior sentiment in the act of buying Activision. (Inferior sentiment in financial context)