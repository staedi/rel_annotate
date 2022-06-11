import streamlit as st
import generic
import frontend

relations_dict = {"Investment": {"Buy": ["Over", "Under"], "Sell": ["Posline"], "IPO": ["Posline"], "Privatize": ["Over", "Under", "Posline"], "Invest": ["Posline"], "Bid": ["Over", "Under"]},
"Family": {"Family": ["Posline"]},
"Cooperation": {"Cooperate": ["Posline"]},
"Performance": {"Perform": ["Over", "Under"], "Inline": ["Posline", "Negline"]},
"Legal": {"File": ["Over"], "Sued": ["Under"], "Indicted": ["Under"], "Subpoenaed": ["Under"], "Alleged": ["Under"], "Win": ["Over"], "Lose": ["Under"]},
"News": {"Launch": ["Posline"], "Patent": ["Posline"], "Authorize": ["Pos", "Neg"]},
"Bankruptcy": {"Bankruptcy": ["Pos", "Neg"]},
"No-rel": {"No-rel": []}}


generic.init_session()
json_lines = generic.read_text()
# next_page = False
frontend.display_sidebar(rel_dict=relations_dict)

prev_page, next_page = frontend.show_pages()
prev_page, next_page, update_status = frontend.display_texts(json_lines=json_lines,pages=[prev_page, next_page],rel_dict=relations_dict)

frontend.save_data(update_status,json_lines)
# generic.write_text(json_lines,save)


# [## Investment (Buy, Sell, IPO, Privatize, Invest, Bid)
# "Over-Buy",   # "A" is bought by B
# "Under-Buy",    # "A" buys B
# "Posline-Sell",   # "A" is sold to B 
# "Posline-IPO",   # "A" IPO
# "Over-Privatize",  # "A" is taken private by B
# "Under-Privatize",    # "A" privatizes B
# "Posline-Privatize",   # "A" is taken private
# "Posline-Invest",   # "A" invested in B
# "Over-Bid",   # "A" wins the bid against B
# "Under-Bid",   # "A" loses the bid to B
# ## Family / Ownership
# "Posline-Family", # "A" Same Family as B
# ## Cooperation (win-win)
# "Posline-Cooperate",   # "A" cooperates with B
# ## Performance (Outperform, Underperform, Inline)
# "Over-Perform",   # "A" outperforms B
# "Under-Perform",   # "A" underperforms B
# "Posline-Inline",    # "A" is inline with B
# "Negline-Inline",    # "A" is inline with B
# ## Legal (File, Indicted, Subpoenaed, Alleged, Win, Lose)
# "Over-File",    # "A" files a lawsuit against B
# "Under-Sued",    # "A" is sued by B
# "Under-Indicted",    # "A" is indicted by B
# "Under-Subpoenaed",    # "A" is subpoenaed by B
# "Under-Alleged",    # "A" is alleged by B
# "Over-Win", # "A" wins against B
# "Under-Lose", # "A" loses to B
# ## News release (Launch, Patent, Authorize)
# "Posline-Launch",    # "A" launches B
# "Posline-Patent",   # "A" files a patent for B
# "Pos-Authorize",   # "A" is authorized by B [Medecin]
# "Neg-Authorize",   # "A" not authorized by B [Medecin]
# ## Bankruptcy
# "Pos-Bankruptcy", # "A" exits bankrupt
# "Neg-Bankruptcy",  # "A" goes bankrupt
# "No-rel"]