import json

import typer
from pathlib import Path

from spacy.tokens import Span, DocBin, Doc
from spacy.vocab import Vocab
from wasabi import Printer

msg = Printer()

SYMM_LABELS = ["Binds"]
MAP_LABELS = {
    ## Business (Found, Buy, Sell, Merge, Operate, IPO, Privatize, Invest, Cancel, Bid)
    # Found (Posline)
    "Posline-Found": "Founded",     # "A" founded B / "A" is founded by B
    # Buy (Over, Under, Posline, Pos)
    "Over-Buy": "Is Bought (by)",   # * "A" is bought by B
    "Under-Buy": "Buys",            # "A" buys B
    "Posline-Buy": "Buys",          # "A" buys B
    "Pos-Buy": "Is Bought (by)",    # "A" is bought by B
    # Sell (Over, Under, Posline, Negline, Pos, Neg) - Distinction ?
    "Over-Sell": "Is Sold (to)",    # "A" is sold to B
    "Under-Sell": "Is Sold (to)",   # "A" is sold to B
    "Posline-Sell": "Sells",        # "A" sells B
    "Negline-Sell": "Is Sold (to)", # "A" is sold to B
    "Pos-Sell": "Sells",            # "A" sells B / "A" is sold to B
    "Neg-Sell": "Sells",            # "A" sells B
    # Merge (Posline, Pos) - Distinction ?
    "Posline-Merge": "Is Merged (with)",    # "A" is merged with B
    "Pos-Merge": "Is Merged (with)",        # "A" is merged with B
    # Operate (Posline, Negline, Pos, Neg)
    "Posline-Operate": "Increased operation (of)",  # "A" increased operation of B
    "Negline-Operate": "Decreased operation (of)",  # "A" decreased operation of B
    "Pos-Operate": "Increased operation",                   # "A" increased operation
    "Neg-Operate": "Decreased operation",                   # "A" decreased operation (+ recall)
    # IPO (Posline)
    "Posline-IPO": "IPO",   # "A" IPO
    # Privatize (Over, Under, Posline)
    "Over-Privatize": "Is Taken Private (by)",  # "A" is taken private by B
    "Under-Privatize": "Privatizes",            # "A" privatizes B
    "Posline-Privatize": "Privatizes",          # "A" privatizes
    # Invest (Posline)
    "Posline-Invest": "Invests / Is Invested (by)", # "A" invested in B / "A" is invested by B ?
    # Cancel (Neg, Over)
    "Neg-Cancel": "Cancels",        # "A" cancels B / "A" is canceled by B / "A" rejects (denies) "B"
    "Over-Cancel": "Cancels",       # "A" cancels B ("A" doesn't support B) / "A" leaves B
    # Bid (Over, Under, Pos)
    "Over-Bid": "Wins the Bid (against)",   # "A" wins the bid against B
    "Under-Bid": "Loses the Bid (to)",      # "A" loses the bid to B
    "Pos-Bid": "Wins the Bid (in)",         # "A" wins the bid in B
    ## Family / Ownership
    "Posline-Family": "Same Family as",     # "A" Same Family as B
    ## Cooperation (win-win)
    "Posline-Cooperate": "Cooperates with", # "A" cooperates with B / "A" uses B
    ## Performance (Outperform, Underperform, Inline, Rate)
    # Perform (Over, Under, Pos, Neg)
    "Over-Perform": "Outperforms",          # "A" outperforms B
    "Under-Perform": "Underperforms",       # "A" underperforms B
    "Pos-Perform": "Performs well",         # "A" performs well
    "Neg-Perform": "Performs bad",          # "A" performs bad
    # Inline (Posline, Negline)
    "Posline-Inline": "Performs positively as",   # "A" performs positively as B
    "Negline-Inline": "Performs negatively as",   # "A" performs negatively as B
    # Rate (Over, Under, Posline, Negline, Pos, Neg)
    "Over-Rate": "Undervalue",              # "A" undervalues B
    "Posline-Rate": "Recognizes",           # "A" recognizes B
    "Negline-Rate": "Is Undervalued as",    # "A" is undervalued as B
    "Pos-Rate": "Is Recognized (by)",       # "A" is recognized by B
    "Neg-Rate": "Is Undervalued (by)",      # "A" is undervalued by B
    ## Recruitment (Hire, Fire, Quit, Lose)
    # Hire (Over, Posline)
    "Over-Hire": "Hires from",  # "A" hires from B
    "Posline-Hire": "Hires",    # "A" hires B
    # Fire
    "Over-Fire": "Fires",   # "A" fires B
    # Quit
    "Over-Quit": "Quits",   # "A" quits B
    # Lose
    "Under-Lose": "Loses (to)", # "A" loses (to) B
    ## Legal (File, Indicted, Subpoenaed, Alleged, Win, Lose)
    "Over-File": "Files a lawsuit (against)",   # "A" files a lawsuit against B
    "Over-Regulate": "Regulates",               # "A" regulates B
    "Neg-Sued": "Is Sued (by)",                 # "A" is sued (by) B
    "Under-Sued": "Is Sued by",                 # "A" is sued by B
    "Neg-Indicted": "Is Indicted (by)",         # "A" is indicted (by) B
    "Under-Indicted": "Is Indicted by",         # "A" is indicted by B
    "Neg-Subpoenaed": "Is Subpoenaed (by)",     # "A" is subpoenaed (by) B
    "Under-Subpoenaed": "Is Subpoenaed by",     # "A" is subpoenaed by B
    "Neg-Alleged": "Is alleged (by)",           # "A" is alleged (by) B
    "Under-Alleged": "Is alleged by",           # "A" is alleged by B
    "Negline-Alleged": "Is alleged as",       # "A" is alleged as B
    "Pos-Win": "Wins (in)",                     # "A" wins (in) B
    "Over-Win": "Wins against",                 # "A" wins against B
    "Neg-Lose": "Loses (in)",                   # "A" loses (in) B
    "Under-Lose": "Loses to",                   # "A" loses to B
    "Posline-Verdict": "Allows",                # "A" allows B 
    "Over-Verdict": "Disallows",                # "A" disallows B
    "Neg-Anger": "Angers",                      # "A" angers B 
    "Over-Anger": "Lashes out at",              # "A" lashes out at B
    "Over-Press": "Urges",                      # "A" urges B 
    "Posline-Settle": "Settles",                # "A" settles B 
    "Pos-Settle": "Settles (with)",             # "A" settles (with) B
    "Negline-Ordered": "Is Ordered as",         # "A" is ordered as B
    "Neg-Ordered": "Is Ordered (by)",           # "A" is ordered by B
    ## News release (Launch, Patent, Authorize)
    "Posline-Launch": "Launches (as)",          # "A" launches (as) B
    "Posline-Patent": "Files a patent (for)",   # "A" files a patent for B
    "Pos-Authorize": "Is authorized (by)",      # "A" is authorized by B [Medecin]
    "Neg-Authorize": "Not authorized (by)",     # "A" not authorized by B [Medecin]
    ## Bankruptcy
    "Pos-Bankruptcy": "Exits bankrupt", # "A" exits bankrupt
    "Neg-Bankruptcy": "Goes bankrupt",  # "A" goes bankrupt
    "No-rel": "Unrelated",
}


# {
#     ## Investment (Buy, Sell, IPO, Privatize, Invest, Bid)
#     "Over-Buy": "Is Bought (by)",   # "A" is bought by B
#     "Under-Buy": "Buys",    # "A" buys B
#     "Posline-Sell": "Is Sold (by)",   # "A" is sold to B 
#     "Posline-IPO": "IPO",   # "A" IPO
#     "Over-Privatize": "Is Taken Private by",  # "A" is taken private by B
#     "Under-Privatize": "Privatizes",    # "A" privatizes B
#     "Posline-Privatize": "Is Taken Private",   # "A" is taken private
#     "Posline-Invest": "Invested",   # "A" invested in B
#     "Over-Bid": "Wins the Bid (against)",   # "A" wins the bid against B
#     "Under-Bid": "Loses the Bid (to)",   # "A" loses the bid to B
#     ## Family / Ownership
#     "Posline-Family": "Same Family as", # "A" Same Family as B
#     ## Cooperation (win-win)
#     "Posline-Cooperate": "Cooperates with",   # "A" cooperates with B
#     ## Performance (Outperform, Underperform, Inline)
#     "Over-Perform": "Outperforms",   # "A" outperforms B
#     "Under-Perform": "Underperforms",   # "A" underperforms B
#     "Posline-Inline": "Is Inline (with)",    # "A" is inline with B
#     "Negline-Inline": "Is Inline (with)",    # "A" is inline with B
#     ## Legal (File, Indicted, Subpoenaed, Alleged, Win, Lose)
#     "Over-File": "Files a lawsuit (against)",    # "A" files a lawsuit against B
#     "Under-Sued": "Is sued (by)",    # "A" is sued by B
#     "Under-Indicted": "Is indicted (by)",    # "A" is indicted by B
#     "Under-Subpoenaed": "Is subpoenaed (by)",    # "A" is subpoenaed by B
#     "Under-Alleged": "Is alleged (by)",    # "A" is alleged by B
#     "Over-Win": "Wins (against)", # "A" wins against B
#     "Under-Lose": "Loses (to)", # "A" loses to B
#     ## News release (Launch, Patent, Authorize)
#     "Posline-Launch": "Launches",    # "A" launches B
#     "Posline-Patent": "Files a patent (for)",   # "A" files a patent for B
#     "Pos-Authorize": "Is authorized (by)",   # "A" is authorized by B [Medecin]
#     "Neg-Authorize": "Not authorized (by)",   # "A" not authorized by B [Medecin]
#     ## Bankruptcy
#     "Pos-Bankruptcy": "Exits bankrupt", # "A" exits bankrupt
#     "Neg-Bankruptcy": "Goes bankrupt",  # "A" goes bankrupt
#     "No-rel": "Unrelated",
# }


def main(json_loc: Path, train_file: Path, dev_file: Path, test_file: Path):
# def main(json_loc: Path, dev_file: Path):
    """Creating the corpus from the Prodigy annotations."""
    Doc.set_extension("rel", default={})
    vocab = Vocab()

    docs = {"train": [], "dev": [], "test": []}
    ids = {"train": set(), "dev": set(), "test": set()}
    count_all = {"train": 0, "dev": 0, "test": 0}
    count_pos = {"train": 0, "dev": 0, "test": 0}

    with json_loc.open("r", encoding="utf8") as jsonfile:
        for line in jsonfile:
            example = json.loads(line)
            span_starts = set()
            if example["answer"] == "accept":
                neg = 0
                pos = 0
                # try:
                # Parse the tokens
                words = [t["text"] for t in example["tokens"]]
                spaces = [t["ws"] for t in example["tokens"]]
                doc = Doc(vocab, words=words, spaces=spaces)

                # Parse the entities
                spans = example["spans"]
                entities = []
                span_end_to_start = {}
                for span in spans:
                    entity = doc.char_span(
                        span["start"], span["end"], label=span["label"]
                    )
                    span_end_to_start[span["token_end"]] = span["token_start"]
                    entities.append(entity)
                    span_starts.add(span["token_start"])
                doc.ents = entities

                # Parse the relations
                rels = {}
                for x1 in span_starts:
                    for x2 in span_starts:
                        rels[(x1, x2)] = {}
                relations = example["relations"]
                for relation in relations:
                    # the 'head' and 'child' annotations refer to the end token in the span
                    # but we want the first token
                    start = span_end_to_start[relation["head"]]
                    end = span_end_to_start[relation["child"]]
                    label = relation["label"]
                    label = MAP_LABELS[label]
                    if label not in rels[(start, end)]:
                        rels[(start, end)][label] = 1.0
                        pos += 1
                    if label in SYMM_LABELS:
                        if label not in rels[(end, start)]:
                            rels[(end, start)][label] = 1.0
                            pos += 1

                # The annotation is complete, so fill in zero's where the data is missing
                for x1 in span_starts:
                    for x2 in span_starts:
                        for label in MAP_LABELS.values():
                            if label not in rels[(x1, x2)]:
                                neg += 1
                                rels[(x1, x2)][label] = 0.0
                doc._.rel = rels

                # only keeping documents with at least 1 positive case
                if pos > 0:
                    docs["dev"].append(doc)
                    count_pos["dev"] += pos
                    count_all["dev"] += pos + neg
                    
                #         # use the original PMID/PMCID to decide on train/dev/test split
                #         article_id = example["meta"]["source"]
                #         article_id = article_id.replace("BioNLP 2011 Genia Shared Task, ", "")
                #         article_id = article_id.replace(".txt", "")
                #         article_id = article_id.split("-")[1]
                #         if article_id.endswith("4"):
                #             ids["dev"].add(article_id)
                #             docs["dev"].append(doc)
                #             count_pos["dev"] += pos
                #             count_all["dev"] += pos + neg
                #         elif article_id.endswith("3"):
                #             ids["test"].add(article_id)
                #             docs["test"].append(doc)
                #             count_pos["test"] += pos
                #             count_all["test"] += pos + neg
                #         else:
                #             ids["train"].add(article_id)
                #             docs["train"].append(doc)
                #             count_pos["train"] += pos
                #             count_all["train"] += pos + neg
                # except KeyError as e:
                #     msg.fail(f"Skipping doc because of key error: {e} in {example['meta']['source']}")

    # docbin = DocBin(docs=docs["train"], store_user_data=True)
    # docbin.to_disk(train_file)
    # msg.info(
    #     f"{len(docs['train'])} training sentences from {len(ids['train'])} articles, "
    #     f"{count_pos['train']}/{count_all['train']} pos instances."
    # )

    docbin = DocBin(docs=docs["dev"], store_user_data=True)
    docbin.to_disk(dev_file)
    msg.info(
        f"{len(docs['dev'])} dev sentences from {len(ids['dev'])} articles, "
        f"{count_pos['dev']}/{count_all['dev']} pos instances."
    )

    # docbin = DocBin(docs=docs["test"], store_user_data=True)
    # docbin.to_disk(test_file)
    # msg.info(
    #     f"{len(docs['test'])} test sentences from {len(ids['test'])} articles, "
    #     f"{count_pos['test']}/{count_all['test']} pos instances."
    # )


if __name__ == "__main__":
    typer.run(main)
