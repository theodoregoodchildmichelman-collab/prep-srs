#!/usr/bin/env python3
"""One-time rework (2026-11-18): rewrite every active C card as a quick-answer card.

Each card keeps its full answer (`a`, used for the verdict and the one-line correction);
only the question changes, into numbered parts answered with a letter, a number, an arrow
or a few words, plus a short `key` with the expected answer. Old questions are saved in
archive/c-card-questions-before-2026-11-18.json. Run once from the repo root.
"""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECK = os.path.join(HERE, "cards.json")
ARCH = os.path.join(HERE, "archive", "c-card-questions-before-2026-11-18.json")

Q = {
"C001": ("\"The treaty fails unless the Senate consents.\" 1) Arrow? 2) Contrapositive? 3) Trap: (a) converse 'fails → no consent' (b) contrapositive (c) none. 4) Consent is (n)ecessary or (s)ufficient?",
         "1 no consent → fails · 2 not fail → consented · 3 a · 4 n"),
"C002": ("\"Every country hosting the program >5 years saw an increase. Z saw no increase.\" 1) What follows about Z (≤6 words)? 2) Could Z have hosted exactly 5 years? y/n",
         "1 not hosted more than 5 years · 2 y"),
"C003": ("Four-day-week firms report higher satisfaction, so a four-day week would raise it at Meridian. 1) Test for a necessary assumption (1 word)? 2) The necessary assumption (≤8 words)? 3) Is 'they work fewer total hours' necessary? y/n",
         "1 negate · 2 satisfaction not due entirely to other differences · 3 n"),
"C004": ("RC inference/main point. 1) Which usually wins: (a) strongest claim (b) most modest claim licensed by the passage (c) what the author would agree with? 2) Main-point trap (≤4 words)? 3) Extreme wording usually: win / lose?",
         "1 b · 2 detail promoted to main point · 3 lose"),
"C005": ("\"The ceasefire will hold unless the border is closed.\" 1) Valid: (i) closed → fails or (ii) not closed → holds? 2) Contrapositive? 3) Name the invalid one's type (1 word).",
         "1 ii · 2 fails → border closed · 3 inverse"),
"C006": ("Panel of 2 from 5 officers, 3 Political. 1) P(both Political) as a fraction? 2) 0.6 × 0.6 is wrong because: (a) rounding (b) draws are without replacement (c) order matters?",
         "1 3/5 × 2/4 = 3/10 (30%) · 2 b"),
"C007": ("1) Correct: (a) 'Walking into the embassy, the flag was visible' (b) 'Walking into the embassy, she saw the flag'? 2) Error name (2 words)? 3) Does the passive 'the flag was seen by her' fix it? y/n 4) The test question (≤6 words)?",
         "1 b · 2 dangling modifier · 3 n · 4 who is doing the -ing?"),
"C008": ("X: 6 grain OR 6 cloth; Y: 4 grain OR 2 cloth. 1) Comparative advantage in grain: X/Y? 2) In cloth: X/Y? 3) You compare (a) raw output (b) opportunity costs? 4) A trade price must lie where (≤6 words)?",
         "1 Y · 2 X · 3 b · 4 between the two opportunity costs"),
"C009": ("\"No attaché may enter the compound without clearance.\" 1) Arrow? 2) Contrapositive? 3) Trap type (1 word)? 4) Does 'without' put a NOT on the if-side? y/n",
         "1 enter → clearance · 2 no clearance → can't enter · 3 inverse · 4 n"),
"C010": ("Ratified → Committee-approved; Committee-approved → not opposed by the Secretary; the Secretary opposes the Pacific accord. 1) What must be true (≤6 words)? 2) 'Never submitted to the Committee' is: (a) scope shift (b) too strong. 3) 'The Senate will never ratify it' is: (a) scope shift (b) too strong.",
         "1 Senate has not ratified it · 2 a · 3 b"),
"C011": ("McCulloch v. Maryland (1819). 1) Holding 1 (≤5 words) + clause? 2) Holding 2 (≤5 words) + clause? 3) Chief Justice?",
         "1 Congress may charter a bank; Necessary and Proper (implied powers) · 2 states can't tax federal bank; Supremacy · 3 Marshall"),
"C012": ("A: 12 tractors OR 24 grain; B: 5 tractors OR 15 grain. 1) Step 1 (≤5 words)? 2) Cost of 1 tractor: A = ?, B = ? 3) Comparative advantage in tractors: A/B? 4) Price range (grain per tractor)?",
         "1 write each opportunity cost · 2 A 2, B 3 · 3 A · 4 between 2 and 3"),
"C013": ("1) Arrow: \"The talks continue unless the delegation walks out.\" 2) Arrow: \"No ambassador may sign without the Secretary's approval.\" 3) Which puts a NOT on the if-side: unless / without?",
         "1 not walk out → talks continue · 2 sign → approval · 3 unless"),
"C014": ("A lawyer is faster than her assistant at typing and legal work. 1) Should she delegate typing? y/n 2) Reason (2 words)? 3) Being better at both = (a) absolute (b) comparative advantage? 4) Superpower and ally version (1–2 words)?",
         "1 y · 2 opportunity cost · 3 a · 4 burden-sharing"),
"C015": ("\"The unexamined life is not worth living.\" 1) Arrow? 2) Contrapositive? 3) Examination is (n)ecessary / (s)ufficient / (b)oth? 4) Does it show examination is the only source of value? y/n",
         "1 unexamined → not worth living · 2 worth living → examined · 3 n · 4 n"),
"C016": ("Socratic method. 1) The three steps (1–2 words each)? 2) A case that meets the definition but isn't the thing shows it is not: n / s? 3) A case that is the thing but fails the definition shows it is not: n / s? 4) Name the productive dead end (1 word).",
         "1 define, counterexample, refine/repeat · 2 s (not sufficient) · 3 n (not necessary) · 4 aporia"),
"C017": ("\"The talks continue unless the delegation walks out.\" 1) Contrapositive? 2) Safe with no extra assumption? y/n 3) The converse is (a) safe (b) the trap?",
         "1 talks stop → walked out · 2 y · 3 b"),
"C018": ("5 officers, 3 Political; pick 2 without replacement. 1) The complement of 'at least one Political', in words? 2) Its probability? 3) P(at least one)?",
         "1 neither is Political · 2 2/5 × 1/4 = 1/10 · 3 9/10 (90%)"),
"C019": ("Arrow: no revocation → embassy stays open. Write: 1) converse 2) inverse 3) contrapositive. 4) Which one is equivalent?",
         "1 stays open → no revocation · 2 revocation → doesn't stay open · 3 doesn't stay open → revocation · 4 contrapositive"),
"C020": ("1) 4/6 × 3/5 = ? (fraction, no decimals) 2) First move (1 word)? 3) 4/6 as a decimal is 0.6? y/n",
         "1 2/5 · 2 cancel · 3 n (0.667)"),
"C021": ("If A then B. Valid or invalid, and name: 1) A, so B 2) not B, so not A 3) B, so A 4) not A, so not B",
         "1 valid (affirming antecedent) · 2 valid (contrapositive) · 3 invalid (affirming consequent/converse) · 4 invalid (denying antecedent/inverse)"),
"C022": ("\"A state receives the grant only if it passes the audit.\" 1) Arrow? 2) Is passing the audit sufficient? y/n 3) 'If and only if' claims (1 / 2) directions? 4) Quick test (≤8 words)?",
         "1 grant → audit · 2 n · 3 2 · 4 can the result happen without X?"),
"C023": ("\"Every ally voted yes. Every committee member voted yes.\" 1) Does anything follow about allies and committee members? y/n 2) Arrows link only when ___ of one = ___ of the next? 3) A chain's contrapositive runs: forward / backward?",
         "1 n · 2 end, start · 3 backward"),
"C024": ("\"Most\" + \"most\" of one group of 30. 1) Must some be in both? y/n 2) Smallest 'most' of 30? 3) Minimum overlap (show the sum)? 4) Does 'most + some' force overlap? y/n",
         "1 y · 2 16 · 3 16 + 16 − 30 = 2 · 4 n"),
"C025": ("30 delegates; most attended morning, most attended afternoon; admitted to dinner → attended both. 1) At least 2 attended both? y/n 2) At least 2 admitted? y/n 3) Why not (1 word)?",
         "1 y · 2 n · 3 converse"),
"C026": ("Write the logical opposite: 1) All agreed 2) No one agreed 3) Some agreed 4) Most agreed. 5) Is 'none agreed' the opposite of 'all agreed'? y/n",
         "1 not all agreed · 2 some agreed · 3 none agreed · 4 half or fewer agreed · 5 n"),
"C027": ("Opposite of: 1) 'If the talks collapse, the aid is frozen.' 2) 'No cable is released without approval.' 3) Is 'if collapse, aid NOT frozen' the opposite? y/n",
         "1 talks collapse AND aid not frozen · 2 a cable released AND not approved · 3 n"),
"C028": ("\"Every packet recipient voted yes, so the packet persuaded them.\" 1) What do you write before the choices? 2) Necessary assumption (≤10 words)? 3) A restated premise is a trap because its negation: (a) breaks the conclusion (b) only contradicts a premise?",
         "1 conclusion + gap · 2 some recipients would not have voted yes without it · 3 b"),
"C029": ("\"The ministry sold every armored car last spring; none of the twelve 2020 cars is in those sales records; so none was armored.\" 1) The gap (≤10 words)? 2) Necessary assumption (≤8 words)? 3) Three wrong-answer kinds (1–2 words each)?",
         "1 a 2020 armored car left before last spring · 2 none of the twelve left before then · 3 restatement, too strong, topic not gap"),
"C030": ("\"If aid is cut, most rural clinics close. Aid was cut. So most rural patients lose care.\" 1) Justifies it: (i) clinics close → patients lose care or (ii) clinics open → patients keep care? 2) The other is the (1 word)? 3) The right answer starts at ___ and ends at ___?",
         "1 i · 2 inverse · 3 what the premises deliver; the conclusion's new term"),
"C031": ("\"Critics say the compound is a waste. They are mistaken. It replaces three leases; rent savings will exceed its cost.\" 1) Main conclusion (≤6 words)? 2) Role of the rent-savings sentence (1 word)? 3) Test word?",
         "1 the compound is not a waste · 2 support/premise · 3 because"),
"C032": ("1) Average time per LR question? 2) At what time do you pick, flag and move? 3) Ever leave a blank? y/n 4) The five traps (1–3 words each)?",
         "1 1:20 · 2 2:00 · 3 n · 4 too strong, hedge overreach, half right, restates premise/conclusion, topic not logic (or wrong direction)"),
"C033": ("Athens: \"Justice is only talked about between equals in power.\" 1) Arrow? 2) Is 'if equals, we may talk about justice' the same claim? y/n 3) Conclusion about Melos (≤5 words)?",
         "1 justice talk → equals in power · 2 n · 3 unequal, so no justice talk"),
"C034": ("Melian Dialogue. 1) Athens' position (≤8 words)? 2) Athens' reply to each Melian appeal: fair play → ?, the gods → ?, Sparta → ? (1–3 words each) 3) Does Thucydides endorse it? y/n 4) What follows next (2 words)?",
         "1 strong do what they can, weak suffer · 2 reputation (subjects watching); gods rule where they can too; hope/Sparta acts on interest · 3 n · 4 Sicilian disaster"),
"C035": ("RC: speech X, then event Y right after it, no stated link, 'the placement is deliberate'. 1) 'X caused Y' is which trap? 2) Supported inference (≤8 words)? 3) Is 'Y caused X' licensed? y/n",
         "1 overreach from a hedge · 2 placement invites reader to see X undercut · 3 n"),
"C036": ("A frost destroys half the coffee crop. 1) Which curve shifts, and which way? 2) Price ↑/↓? 3) Quantity traded ↑/↓? 4) The demand side: (a) shifts (b) moves along?",
         "1 supply, left · 2 ↑ · 3 ↓ · 4 b"),
"C037": ("A fad adds buyers while a frost cuts supply. 1) Price: ↑ / ↓ / uncertain? 2) Quantity: ↑ / ↓ / uncertain? 3) Is the equilibrium price an average? y/n",
         "1 ↑ · 2 uncertain · 3 n"),
"C038": ("\"Fare-free weekends raised ridership 30%, so fewer cars came downtown.\" 1) Gap (≤10 words)? 2) Necessary assumption (≤10 words)? 3) Negated, does the conclusion survive? y/n",
         "1 new riders may never have driven · 2 some new riders would otherwise have driven · 3 n"),
"C039": ("1) Staff:cases = 3:5, 40 cases → staff? 2) 40 lawyers split 3:5 → each office? 3) First move in each: scale / add the parts?",
         "1 24 · 2 15 and 25 · 3 first scale (different things), second add the parts (one group)"),
"C040": ("4 officers clear 18 cases in 3 days. 1) Cases per officer-day? 2) Days for 6 officers to clear 54? 3) % change in officers 4 → 6? 4) % change in days for the same job?",
         "1 1.5 · 2 6 · 3 +50% · 4 −33⅓%"),
"C041": ("Tariffs. 1) Which branch holds the power, and where (article/section)? 2) How does a President impose them (≤5 words)? 3) One risk for Congress (≤8 words)?",
         "1 Congress, Art. I §8 · 2 authority delegated by statute · 3 one person changes or waives policy fast"),
"C042": ("1973 oil embargo. 1) Who imposed it? 2) Against whom, after which war? 3) Price roughly ×? 4) Which curve shifted? 5) Short-run oil demand: elastic / inelastic?",
         "1 Arab OPEC (OAPEC), Saudi-led · 2 US and allies; Yom Kippur War · 3 ×4 · 4 supply left · 5 inelastic"),
"C043": ("Sanctions remove a big supplier's oil. 1) Shift? 2) Price ↑/↓, quantity ↑/↓? 3) Price rises more or less than quantity falls? 4) Why it worries a government before elections (≤5 words)?",
         "1 supply left · 2 ↑, ↓ · 3 more (inelastic) · 4 voters feel prices directly"),
"C044": ("1) Opposite of 'translator OR legal adviser'? 2) Opposite of 'closed AND evacuated'? 3) Plain 'or' allows both? y/n",
         "1 neither (no translator AND no adviser) · 2 not closed OR not evacuated · 3 y"),
"C045": ("GRE Text Completion. 1) Step 2 (≤5 words)? 2) Fill: 'A forged signature can ___ a valid contract, stripping it of force.' (a) preclude (b) vitiate (c) obviate 3) Meanings of the other two (1–3 words each)?",
         "1 write your own word first · 2 b · 3 preclude = rule out in advance; obviate = remove a need"),
"C046": ("grant → technical AND budget review; budget review → on time; Harbor was late. 1) What must be true (≤4 words)? 2) 'Would have got it if on time' confuses ___ with ___? 3) 'Every proposal that failed budget review was late' is the (1 word)?",
         "1 Harbor got no grant · 2 necessary, sufficient · 3 converse"),
"C047": ("Supply falls 8%; buyers cut quantity 4% per 10% price rise. 1) Price rise %? 2) Price rises more / less than quantity falls? 3) Three causes of inelastic demand (1–2 words each)?",
         "1 20% · 2 more · 3 necessity, few substitutes, short run"),
"C048": ("1) Product of two consecutive integers: always / sometimes / never even? Reason (≤6 words)? 2) 7,482 divisible by 3? by 9? 3) Prime factorization of 84? 4) n² odd → n odd? y/n",
         "1 always; one of them is even · 2 3 y, 9 n (digit sum 21) · 3 2² × 3 × 7 · 4 y"),
"C049": ("Gas-tax holiday argument (refiners can't expand; inelastic demand; 'pump price will barely move'; 'besides, it costs billions'). 1) Main conclusion with its hedge (≤10 words)? 2) Role of the treasury cost (1 word)? 3) 'Sellers will always raise prices by any tax cut' is which trap?",
         "1 suspending the tax won't noticeably lower pump prices · 2 aside · 3 overreach from a hedge"),
"C050": ("Glaucon's ring of Gyges. 1) What would the just man do with the ring (≤5 words)? 2) Why people are just, on his view (≤5 words)? 3) Socrates must show justice is good ___ and ___?",
         "1 act like the unjust man · 2 fear of punishment/reputation · 3 in itself, for its results"),
"C051": ("1) Glaucon's three kinds of goods (one example each)? 2) Where he wants justice placed (1, 2 or 3)? 3) Socrates' reply in 3 words? 4) Strongest objection (2 words)?",
         "1 for itself (joy), for results (medicine), both (health) · 2 3 · 3 justice = soul's health · 4 calm psychopath"),
"C052": ("GRE Issue. 1) A 4 has (≤4 words)? 2) Three things a 6 adds (2–4 words each)? 3) Thesis shape (fill: X, because ___, except when ___)? 4) A pure yes/no on an 'extent' prompt scores at most?",
         "1 clear position, generic examples · 2 qualified thesis, named examples, strongest counterargument answered · 3 Y, Z · 4 4"),
"C053": ("\"Ridership rose 30%, so fewer cars came downtown.\" 1) Conclusion clause? 2) Where the gap sits (≤6 words)? 3) 'The weekends caused the rise' is a trap because it (1–2 words)?",
         "1 fewer cars came downtown · 2 between evidence and conclusion · 3 restates the premise"),
"C054": ("Harbor Tunnel: rule about who BENEFITS; evidence about public funding. 1) Conclusion (≤6 words)? 2) The term shift (2 words → 2 words)? 3) Necessary assumption (≤8 words)? 4) 'Paid entirely from public funds' is which trap?",
         "1 don't build the tunnel · 2 who benefits → who pays · 3 benefits go mainly to the wealthy · 4 restates a premise"),
"C055": ("Retirement age: analysts say it will 'inevitably hurt' manual workers; author: a partial early pension could protect them. 1) Main conclusion with its hedge? 2) 'Will not hurt manual workers' is which trap?",
         "1 a higher age need not hurt manual workers · 2 overreach from a hedge"),
"C056": ("Mentoring: joiners 9% dropout vs 14% for others; dean: the program works. 1) Gap (1–2 words)? 2) Necessary assumption (≤10 words)? 3) The restated premise's negation: (a) breaks the conclusion (b) only contradicts a premise? 4) Opposite of 'fewer'?",
         "1 self-selection · 2 joiners weren't already less likely to drop out · 3 b · 4 not fewer"),
"C057": ("\"Course → night shift. Priya has worked here 3 years. So Priya gets the night shift.\" 1) Add what (an arrow)? 2) Is a too-strong rule a flaw on these items? y/n 3) Two real traps (1 word each)?",
         "1 worked 3 years → completed course (or 'Priya completed it') · 2 n · 3 converse/inverse, merely necessary"),
"C058": ("Signs → goes to the Secretary; the cable is a report she drafted. 1) Bridge: (i) drafts → signs (ii) signs → drafts (iii) not signed → not sent? 2) Names of the other two? 3) Water rule 'secret → harms security': which assumption makes 'publish' follow (≤5 words)?",
         "1 i · 2 ii converse, iii inverse · 3 publishing would not harm security"),
"C059": ("\"Although critics dismissed the proposal as (i)___, even they conceded its budget analysis was (ii)___.\" 1) (i) fatuous / trenchant / exigent 2) (ii) trenchant / spurious / perfidious 3) Which blank do you start with (1 word)?",
         "1 fatuous · 2 trenchant · 3 easier"),
"C060": ("Grain sells 100 sacks at 10; a ceiling of 6 → supply 60, demand 140. 1) The 80-sack gap is a? 2) Lost trades (number)? 3) New buyers (number)? 4) Deadweight loss = (a) the lost trades (b) the shortage (c) the gains lost on the lost trades?",
         "1 shortage · 2 40 · 3 40 · 4 c"),
"C061": ("1) Who bears most of a tax: more / less elastic side? 2) Does the legal payer matter? y/n 3) Inelastic buyers → deadweight loss: small / large?",
         "1 less elastic · 2 n · 3 small"),
"C062": ("Bike lanes painted, sales fell 8%; owners blame the lanes; removing them will restore sales. 1) Main conclusion? 2) General gap (≤10 words)? 3) Is 'other streets did not fall similarly' necessary? y/n",
         "1 removing the lanes will restore sales · 2 decline not due to a cause that stays after removal · 3 n"),
"C063": ("Aristotle's six regimes. 1) Two sorting questions (2–3 words each)? 2) Sound / deviant for one, few, many? 3) Which matters more: number / interest? 4) Most stable regime leans on (2 words)?",
         "1 how many rule; in whose interest · 2 kingship/tyranny, aristocracy/oligarchy, polity/democracy · 3 interest · 4 middle class"),
"C064": ("1) 6-level thesis shape (fill: claim, because ___, except when ___)? 2) Max words? 3) The except-when must name a case where (a) the main claim is strongest (b) the opposing view wins?",
         "1 reason, limit · 2 40 · 3 b"),
"C065": ("1) Thesis: how many sentences and max words? 2) Must the except-when (a) limit or (b) support the claim? 3) The sharp idea on future generations (≤5 words)?",
         "1 1, 40 · 2 a · 3 through consent, not over it"),
"C066": ("Prompt: put X AHEAD OF Y. 1) 'If they always did it, no one would be served' attacks which reading (1 word)? 2) Better move (≤6 words)? 3) Example test (≤8 words)?",
         "1 always/extreme · 2 take a position on WHEN · 3 does it support the point you use it for?"),
"C067": ("Democracy and the unborn. 1) Why it's hard (≤8 words)? 2) Act for the future ___ consent, not ___ it? 3) Possible exception (≤5 words)?",
         "1 the will of the unborn can't be known · 2 through, over · 3 irreversible existential threat"),
"C068": ("Critic: X is a waste (low count). Author: count was taken in exam week, so it can't show X is a waste, so the council should wait. 1) Main conclusion? 2) Role of 'it can't show X is a waste': C / I / P / O? 3) Can a concession be the conclusion? y/n",
         "1 the council should wait · 2 I (intermediate) · 3 n"),
"C069": ("1) Stock (≤4 words)? Flow (≤4 words)? 2) Debt 30T, deficit fell 1.5T → 1.0T: did the debt fall by a third? y/n What did it do? 3) Lake loses 1M L/month; outflow cut by 0.5M: still shrinking? y/n",
         "1 amount at a moment; amount per unit time · 2 n, rose by 1T · 3 y (half the pace)"),
"C070": ("GRE Sentence Equivalence. 1) Pick how many of how many? 2) The two must ___ and ___? 3) The three traps (2–4 words each)?",
         "1 2 of 6 · 2 fit the sentence, mean the same · 3 fits but no partner; pair that doesn't fit; both fit but differ"),
"C071": ("1) GCD of 12 and 18? 2) LCM? 3) The check (≤5 words)? 4) n leaves remainder 4 on ÷6: remainder of n + 5?",
         "1 6 · 2 36 · 3 GCD × LCM = product · 4 3"),
"C072": ("A and B go together; the author says A causes B. 1) The four rivals to rule out (1–2 words each)? 2) Regression to the mean is a form of which rival? 3) General gap (≤6 words)?",
         "1 reverse, common cause, measurement, coincidence · 2 coincidence · 3 nothing else explains it"),
"C073": ("10 lowest schools got breakfast; scores rose 6. 1) Best weakener type (≤4 words)? 2) 'Other 30 unchanged': weakens / strengthens / irrelevant? 3) 'The 10 stayed below average': weakens / strengthens / irrelevant?",
         "1 regression to the mean · 2 strengthens · 3 irrelevant"),
"C074": ("US treaties. 1) Who negotiates? 2) Who ratifies, by what vote? 3) What avoids that vote (2 kinds)? 4) Is that an 'executive order'? y/n",
         "1 President · 2 Senate, 2/3 present · 3 executive agreements; congressional-executive agreements · 4 n"),
"C075": ("1) Two reversing signals + one hidden one? 2) Two continuing signals? 3) 'Not merely critical but ___': the blank is (a) weaker (b) stronger? 4) 'Although usually ___ in public, her speech was blunt': circumspect / bellicose / garrulous?",
         "1 although, but (yet/despite); hidden: far from · 2 because, thus (moreover/indeed) · 3 b · 4 circumspect"),
"C076": ("1) The two loop types? 2) Ring test: count ___ arrows; even = ?, odd = ? 3) A delay in a balancing loop causes (≤3 words)? 4) Bank run / thermostat: which type each?",
         "1 reinforcing, balancing · 2 'more → less'; reinforcing, balancing · 3 overshoot, boom-bust · 4 R, B"),
"C077": ("1) −3² = ? (−3)² = ? 2) 2⁻¹ = ? 3) √75 = ? √48 = ? 4) 16^(1/2) = ? 5) Does a negative exponent make a number negative? y/n",
         "1 −9, 9 · 2 1/2 · 3 5√3, 4√3 · 4 4 · 5 n"),
"C078": ("'No hospital qualifies without reporting every incident; Westbrook reports every incident; so it qualifies.' 1) Flaw: treats ___ as ___? 2) 'Only those who pass earn a star; Casa earned one, so it passed': valid / flawed? 3) 'Passing earns a star; Casa didn't earn one, so it didn't pass': valid / flawed?",
         "1 necessary, sufficient · 2 valid · 3 valid"),
"C079": ("Machiavelli, ch. 17. 1) The claim with its hedge (≤12 words)? 2) Why love fails (≤6 words)? 3) What the feared ruler must avoid (1 word), and the two things he must not touch?",
         "1 safer to be feared than loved, if one must be lacking · 2 obligation broken when it pays · 3 hatred; property and women"),
"C080": ("Thesis 'defy popularity for the people'; counter: Stalin and Mao. 1) The limit must be (a) a restatement of 'for the people' (b) a test the dictators could not pass? 2) Example limit (≤8 words)? 3) Form: sentences, max words?",
         "1 b · 2 except when it can't later face democratic scrutiny · 3 1, 40"),
"C081": ("Author reports 'X shows Y', says 'this claim is mistaken', gives a premise, then a 'so' sentence. 1) Main conclusion? 2) The 'so' sentence is usually the (1 word)? 3) Test (≤8 words)? 4) Two scope words to check?",
         "1 X does not show Y · 2 intermediate · 3 which sentence are all others reasons for? · 4 alone, always (never)"),
"C082": ("GRE 'select ALL that apply'. 1) First thing you do (≤4 words)? 2) Partial credit? y/n 3) 'Too specific' is a reason to reject a stated choice? y/n",
         "1 read the instruction line · 2 n · 3 n"),
}


def main():
    deck = json.load(open(DECK, encoding="utf-8"))
    old = {}
    for c in deck["cards"]:
        if c["id"].startswith("C") and c["id"] in Q:
            old[c["id"]] = c["q"]
            c["q"], c["key"] = Q[c["id"]]
            c["history"] = (c.get("history", "").rstrip()
                            + " 2026-11-18: rewritten as a quick-answer card (old question in archive).").strip()
    missing = [c["id"] for c in deck["cards"] if c["id"].startswith("C") and c["id"] not in Q]
    if missing:
        raise SystemExit(f"No rewrite for {missing}")
    with open(ARCH, "w", encoding="utf-8") as f:
        json.dump(old, f, ensure_ascii=False, indent=1)
    with open(DECK, "w", encoding="utf-8") as f:
        json.dump(deck, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"Rewrote {len(old)} C cards")


if __name__ == "__main__":
    main()
