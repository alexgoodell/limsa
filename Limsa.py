
# coding: utf-8

# #Limsa
# _Locally-interacting Markov models for HIV, TB, DM in South Africa_
# 
# This is an IPython/Jupyter notebook. It is a method for creating reproducable research. Essentially, it is a way to show "literate programming", or very well-documented code for scientific processes. It mixes normal text with code blocks that can be run and re-run independently. 
# 
# The purpose of this IPython notebook is to organize the data that will be used to creat the Limsa model in Go. Normally, I would complete this "pre-processing" task in Excel, but I want to try something more detailed and reproducible. 
# 
# This notebook is connected to a python application and database that will store all the tables for the Limsa model. As we progress, we will build these tables. *All changes to the database should be made through this notebook, so a record of all changes is available.* 
# 
# The database has tables:
# * Chains
# * States
# * Transition probabilities
# * Interactions
# * References
# * Raw inputs
# 
# To view the results of the tables, visit: http://limsa.org/admin
# 
# The Go model will then use these tables to run the model.
# 

# In[292]:

from IPython.display import Image
#connect to application
from app import * 
#this gives us access to the database through a variables "db"
def save(thing):
    if thing == None:
        raise ValueError('Nothing to save')
    else:
        db.session.add(thing)
        db.session.commit()
    
# remove any past problematic sessions
db.session.rollback()

# create all tables
db.drop_all()
db.create_all()
    
# drop any chains in db
db.session.query(Chain).delete()
db.session.commit()
    
# drop any states in db
db.session.query(State).delete()
db.session.commit()

# drop any raw inputs in db
db.session.query(Raw_input).delete()
db.session.commit()

# drop any references in db
db.session.query(Reference).delete()
db.session.commit()



def link_tps_to_chains():
    tps = Transition_probability.query.all()
    for tp in tps:
        from_state = tp.From_state
        chain = from_state.Chain
        tp.Chain = chain
        save(tp)
        
def visualize_chain(chain):
    tps = Transition_probability.query.filter_by(Chain=chain).all()
    G=pgv.AGraph(directed=True, rankdir="LR")
    
    for tp in tps:
        G.add_node(tp.From_state.name, shape="box", fontname="ArialMT")
        G.add_node(tp.To_state.name, shape="box", fontname="ArialMT")
        if tp.Is_dynamic:
            G.add_edge(tp.From_state.name, tp.To_state.name, label="Dynamic", fontname="ArialMT", fontsize="10") # adds edge 'b'-'c' (and also nodes 'b', 'c')
        else:
            G.add_edge(tp.From_state.name, tp.To_state.name, label=tp.Tp_base, fontname="ArialMT", fontsize="10") # adds edge 'b'-'c' (and also nodes 'b', 'c')
    G.layout(prog='dot')
    G.draw('file.png')


# First, let's create the different chains the model will need.

# In[293]:

# create the chains we need
chain_names = ['TB disease', 'TB treatment', 'TB resistance',
          'HIV disease', 'HIV treatment', 'HIV risk groups',
          'Setting', 'Diabetes disease and treatment']
for chain_name in chain_names:
    the_chain = Chain(name=chain_name)
    save(the_chain)
    
# print chains from database
Chain.query.all()


# #TB Disease
# 
# Great. Now let's work on the TB disease chain. 
# 
# ###States
# 
# First, let's define the different TB states. Here is our state-transition diagram:
# 
# ![](static/imgs/tb.jpg)

# In[294]:

# get TB chain
tb_chain = Chain.query.filter_by(name="TB disease").first()

# create the chains we need
state_names = ['Uninfected', 'Fast latent', 
                'Slow latent', 'Non-infectious active', 
                'Infectious active', 'Self cure from non-infectious', 
               'Self cure from infectious','Death']
for state_name in state_names:
    the_state = State(name=state_name,chain=tb_chain)
    save(the_state)
    
# print chains from database
State.query.filter_by(chain=tb_chain).all()


# ###Gathering raw inputs
# 
# The transition from ``uninfected`` to any of the infected states is a function of how many people are infected with TB. This will be calculated dynamically, based on the estimated number of contacts and infectivity of contacts. In order to be able to use this data in the Go model, I've created a table called `Raw_inputs`. Let's save this information there. Each Raw_inputs row has a `value`, which represents its base value, as well as a verbose `name`, a `high` and `low`. In addition, there is a `slug`. This is a shortened version of the name, and it will be imported and accessable from the Go code. This is accomplished by begining the project setup with a Makefile (or setup.py) that writes a Go file importing these variables as slugs. Yes - the python program will *write* a Go program.
# 
# It has been shown that people with infectious TB can infect 10-15 people through close contact per year. This can be used to calculate our base case transmissability coefficient, although calibration will be needed.

# In[295]:

# Let's use the mean as the value

low = 10.0
high = 15.0
value = (low+high)/2.0

# First save reference
bibtex = '''
@article{sanchez1997uncertainty,
  title={Uncertainty and sensitivity analysis of the basic reproductive rate: tuberculosis as an example},
  author={Sanchez, Melissa A and Blower, Sally M},
  journal={American Journal of Epidemiology},
  volume={145},
  number={12},
  pages={1127--1137},
  year={1997},
  publisher={Oxford Univ Press}
}
'''

reference = Reference(name="Sanchez 1997",bibtex=bibtex)
save(reference)

# Save input
number_of_infections_per_infected = Raw_input(
    name="Number of TB infections per TB infected",
    slug="number_of_infections_per_infected",
    value=value,
    low=low,
    high=high,
    reference=reference
)
save(number_of_infections_per_infected)


# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 

# We should also create a variable that represents a transmissability coefficient to adjust during calibration

# In[296]:

trans_coeff = Raw_input(name="TB transmissability coefficient")
save(trans_coeff)


# We will also need a variable to represent the % of individuals that become slow vs fast latent.

# In[297]:

## The majority develop slow latent
name = '''
Dye cite Sutherland 1968, 1976 Ferebee 1970, Comstock 1982, Sutherland et al 1982, 
Styblo 1986, Krishnamurthy et al 1976, Krishnamurthy & Chaudhuri 1990, Vynnycky 1996,
Vynnycky & Fine 1997, this study
'''

reference = Reference(name=name)
save(reference)

prop_slow = Raw_input(
    name="Proportion of individuals developing slow latent TB",
    slug="prop_slow",
    value = 0.86,
    low = 0.75,
    high = 0.92,
    reference=reference
)
save(prop_slow)


# Some develop fast latent (ie, progressive disease)
# TODO this may just be calculated as 1-slow 
prop_fast = Raw_input(
    name="Proportion of individuals developing fast latent TB",
    slug="prop_fast",
    value = 0.14,
    low = 0.08,
    high = 0.25,
    reference=reference
)
save(prop_fast)


# Next, we save the rate at which slow latent develop active disease, as an annual figure:

# In[298]:

reference=Reference(name="Dye cite Horwitz et al 1969, Barnett et al 1971, Sutherland et al 1982, Styblo 1991, Vynnycky 1996, Vynnycky & Fine 1997, this study")

rate_slow_annual = Raw_input(
    name="Annual rate at slow latent develop active disease",
    slug="rate_slow_annual",
    value=0.00013,
    low=0.00010,
    high=0.00030,
    reference=reference)

save(rate_slow_annual)


# Similarly, we have a rate at which fast latent develop active disease
# 
# 

# In[299]:

reference=Reference(name="Basu cites: [5, 6, 18]")

rate_fast_annual = Raw_input(
    name="Annual rate at fast latent develop active disease",
    slug="rate_fast_annual",
    value=0.88,
	low=0.76,
    high=0.99,
    reference=reference)

save(rate_fast_annual)


# It is also estimated that 65% of cases are infectious

# In[300]:

reference=Reference(name="Dye cites: Styblo 1977, Murray et al 1993, Barnett & Styblo 1991")

prop_infectious = Raw_input(
    name="Proportion of active cases that are infectious",
    slug="prop_infectious",
    value=0.65,
    low=0.50,
    high=0.65,
    reference=reference
)

save(prop_infectious)


# This is also a rate of self-cure.

# In[301]:

reference=Reference(name="Dye cites: Springett 1971, Olakowski 1973, NTI 1974, Enarson & Rouillon 1994, Grzybowski & Enarson 1978")

rate_self_cure_annual = Raw_input(
    name="Annual rate of self-cure",
    slug="rate_self_cure_annual",
    value=0.020,
    low=0.15,
    high=0.25,
    reference=reference
)

save(rate_self_cure_annual)


# And an ability to replase from self cure

# In[302]:

reference=Reference(name="Dye cites: Springett 1961, Grzybowski et al 1965, Ferebee 1970, Chan-Yeung et al 1971, Campbell 1974, Nakielna et al 1975, Styblo 1986")

rate_relapse_from_self_cure_annual = Raw_input(
    name="Annual rate of relapse from self-cure",
    slug="rate_relapse_from_self_cure_annual",
    value=0.03,
    low=0.02,
    high=0.04,
    reference=reference
)

save(rate_relapse_from_self_cure_annual)


# Individuals can also convert from non-infectious to infection at a specified rate

# In[ ]:




# In[303]:

reference = Reference(name="Dye cites Ferebee 1970, HKCS 1974")

rate_conversion_annual = Raw_input(
    name="Annual rate of conversion from non-infectious to infectious",
    slug="rate_conversion_annual",
    value = 0.015,
    low =0.007,
    high = 0.02,
    reference=reference)

save(rate_conversion_annual)


# ####Mortality
# 
# Individuals can die of infectious active TB as well as non-infectious active TB.

# In[304]:

#### infectious TB
reference = Reference(name="Dye who cites Rutledge & Crouch 1919, Berg 1939, Drolet 1938, Thompson 1943, Tatersall 1947, Lowe 1954, Springett 1971, NTI 1974, Grzybowski & Enarson 1978")

infect_tb_mort_annual = Raw_input(
    name="Yearly mortality from infectious TB",
    slug="infect_tb_mort_annual",
    value=0.30,
    low=0.20,
    high=0.40,
    reference=reference
)
save(infect_tb_mort_annual)

reference = Reference(name="Dye who cites Lindhart 1939, Murray et al 1993")

noninfect_tb_mort_annual = Raw_input(
    name="Yearly mortality from non-infectious TB",
    slug="noninfect_tb_mort_annual",
    value=0.21,
    low=0.18,
    high=0.25,
    reference=reference
)

save(noninfect_tb_mort_annual)


# ### Transition probabilities
# 
# Now, we can fill in the basic transition probabilties for this chain. 

# In[305]:

# For later visualizaton scripts
import pygraphviz as pgv
import time


# In order to convert yearly rates to quarterly rates, we use the following function
# TODO this is not really true - to discuss
def convert_year_to_qt(value):
    return value/4


# TODO: Run PSA changes here?

# TODO: should there be a function that fills in recursive TPs?

# get all states of the TB disease chain
uninfected_state=State.query.filter_by(name="Uninfected",chain=tb_chain).first()
fast_latent_state=State.query.filter_by(name="Fast latent",chain=tb_chain).first()
slow_latent_state=State.query.filter_by(name="Slow latent", chain=tb_chain).first()
noninfectious_active_state=State.query.filter_by(name="Non-infectious active", chain=tb_chain).first()
infectious_active_state=State.query.filter_by(name="Infectious active", chain=tb_chain).first()
self_cure_from_noninfectious = State.query.filter_by(name="Self cure from non-infectious", chain=tb_chain).first()
self_cure_from_infectious = State.query.filter_by(name="Self cure from infectious", chain=tb_chain).first()
death_state=State.query.filter_by(name="Death", chain=tb_chain).first()

#Infection to fast latent
save(Transition_probability(
    From_state=uninfected_state,
    To_state=fast_latent_state,
    Is_dynamic=True
))




# Infection to slow latent
save(Transition_probability(
    From_state=uninfected_state,
    To_state=slow_latent_state,
    Is_dynamic=True
))

# Slow latent to non-infectious active

slow_to_noninfectious_active = convert_year_to_qt(rate_slow_annual.value*(1.0-prop_infectious.value))

save(Transition_probability(
    From_state=slow_latent_state,
    To_state=noninfectious_active_state,
    Tp_base=slow_to_noninfectious_active
))

# Slow latent to infectious active

slow_to_infectious_active = convert_year_to_qt(rate_slow_annual.value*prop_infectious.value)

save(Transition_probability(
    From_state=slow_latent_state,
    To_state=infectious_active_state,
    Tp_base=slow_to_infectious_active
))

# Fast latent to non-infectious active

fast_to_noninfectious_active = convert_year_to_qt(rate_fast_annual.value*(1.0-prop_infectious.value))

save(Transition_probability(
    From_state=fast_latent_state,
    To_state=noninfectious_active_state,
    Tp_base=fast_to_noninfectious_active
))

# Fast latent to infectious active

fast_to_infectious_active = convert_year_to_qt(rate_fast_annual.value*prop_infectious.value)

save(Transition_probability(
    From_state=fast_latent_state,
    To_state=infectious_active_state,
    Tp_base=fast_to_infectious_active
))

# Self cure - infectious

rate_self_cure_qt = convert_year_to_qt(rate_self_cure_annual.value)

save(Transition_probability(
    From_state=infectious_active_state,
    To_state=self_cure_from_infectious,
    Tp_base=rate_self_cure_qt
))

# Self cure - noninfectious

rate_self_cure_qt = convert_year_to_qt(rate_self_cure_annual.value)

save(Transition_probability(
    From_state=noninfectious_active_state,
    To_state=self_cure_from_noninfectious,
    Tp_base=rate_self_cure_qt
))

# Relapse from self cure - infectious

rate_relapse_from_self_cure_qt = convert_year_to_qt(rate_relapse_from_self_cure_annual.value)

save(Transition_probability(
    From_state=self_cure_from_infectious ,
    To_state=infectious_active_state,
    Tp_base=rate_relapse_from_self_cure_qt
))

# Replase from self cure - noninfectious

rate_relapse_from_self_cure_qt = convert_year_to_qt(rate_relapse_from_self_cure_annual.value)

save(Transition_probability(
    From_state=self_cure_from_noninfectious,
    To_state=noninfectious_active_state,
    Tp_base=rate_relapse_from_self_cure_qt
))


# Conversion from non-infectious to infectious

rate_conversion_qt = convert_year_to_qt(rate_conversion_annual.value)

save(Transition_probability(
    From_state=noninfectious_active_state,
    To_state=infectious_active_state,
    Tp_base=rate_conversion_qt
))


# Mortality - from noninfectious

noninfect_tb_mort_qt = convert_year_to_qt(noninfect_tb_mort_annual.value)

save(Transition_probability(
    From_state=noninfectious_active_state,
    To_state=death_state,
    Tp_base=noninfect_tb_mort_qt
))

# Mortality - from infectious

infect_tb_mort_qt = convert_year_to_qt(infect_tb_mort_annual.value)

save(Transition_probability(
    From_state=infectious_active_state,
    To_state=death_state,
    Tp_base=infect_tb_mort_qt
))


# Now that we've completed building the transitions matrix, we can visualize all the transitions (recursive transitions not shown).

# In[306]:

link_tps_to_chains()
visualize_chain(tb_chain)
Image(filename='file.png')


# #TB resistance
# 
# Next, let's move on to discuss TB resistance. We want to model an uninfected state, as well as five different diseased states:
# 
# * Fully Susceptible
# * INH-monoresistant
# * RIF-monoresistant
# * MDR
# * XDR
# 
# Let's get the chain for resistance, and add these states to the chain.

# In[307]:

# get TB resistance chain
tb_resistance_chain = Chain.query.filter_by(name="TB resistance").first()

# create the chains we need
state_names = ["Uninfected","Fully Susceptible","INH-monoresistant",
               "RIF-monoresistant","MDR","XDR"]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=tb_resistance_chain)
    save(the_state)
    
# print chains from database
State.query.filter_by(chain=tb_resistance_chain).all()


# ##Gathering raw inputs
# 
# The transition probabilities for aquiring a resistant infection are the sum of:
# * the chance of your current strain becoming endogenously resistant
# * the chance you will become infected with a drug-resistant strain from someone else
# 
# The later will need to be calculated dynamically, but we can store the former as raw input to be used by the model. Let's do that.

# In[308]:

reference = Reference(name="Basu calibration")

# DS -> INHR

endo_rate_ds_to_inhr_annual = Raw_input(
    name="Annual rate of endogenous conversion from drug-suseptible to INH resistant",
    slug="endo_rate_ds_to_inhr_annual",
    value=0.038,
    low=0.025,
    high=0.050,
    reference=reference
)

save(endo_rate_ds_to_inhr_annual)

# DS -> RIFR

endo_rate_ds_to_rifr_annual = Raw_input(
    name="Annual rate of endogenous conversion from drug-suseptible to RIF resistant",
    slug="endo_rate_ds_to_rifr_annual",
    value=0.038,
    low=0.025,
    high=0.050,
    reference=reference 
)

save(endo_rate_ds_to_rifr_annual)

# RIFR -> MDR

endo_rate_rifr_to_mdr_annual = Raw_input(
    name="Annual rate of endogenous conversion from RFI resistant to MD resistant",
    slug="endo_rate_rifr_to_mdr_annual",
    value=0.038,
    low=0.025,
    high=0.050,
    reference=reference 
)

save(endo_rate_rifr_to_mdr_annual)

# INHR -> MDR

endo_rate_inhr_to_mdr_annual = Raw_input(
	 name="Annual rate of endogenous conversion from INHR to MD resistant",
    slug="endo_rate_inhr_to_mdr_annual",
    value=0.038,
	 low=0.025,
	 high=0.050,
	 reference=reference 
)

save(endo_rate_inhr_to_mdr_annual)

# MDR->XDR

endo_rate_mdr_to_xdr_annual = Raw_input(
    name="Annual rate of endogenous conversion from MDR to XD resistant",
    slug="endo_rate_mdr_to_xdr_annual",
    value=0.030,
    low=0.025,
    high=0.050,
    reference=reference 
)

save(endo_rate_mdr_to_xdr_annual)


# ## Transition probabilities
# 
# As mentioned above, these will need to be calcualted dynamically. Let's add them in, but mark them all as dynamic.

# In[309]:


# get TB resistance chain
tb_resistance_chain = Chain.query.filter_by(name="TB resistance").first()

# Get states
uninfected_state=State.query.filter_by(name="Uninfected",chain=tb_resistance_chain).first()
fully_susceptible_state=State.query.filter_by(name="Fully Susceptible",chain=tb_resistance_chain).first()
inh_monoresistant_state=State.query.filter_by(name="INH-monoresistant", chain=tb_resistance_chain).first()
rif_monoresistant_state=State.query.filter_by(name="RIF-monoresistant", chain=tb_resistance_chain).first()
mdr_state=State.query.filter_by(name="MDR", chain=tb_resistance_chain).first()
xdr_state=State.query.filter_by(name="XDR", chain=tb_resistance_chain).first()

# Uninfected to infected
save(Transition_probability(
    From_state=uninfected_state,
    To_state=fully_susceptible_state,
    Is_dynamic=True
))

# DS to RIF
save(Transition_probability(
    From_state=fully_susceptible_state,
    To_state=rif_monoresistant_state,
    Is_dynamic=True
))

# DS to INHR
save(Transition_probability(
    From_state=fully_susceptible_state,
    To_state=inh_monoresistant_state,
    Is_dynamic=True
))

#  RIF to MDR
save(Transition_probability(
    From_state=rif_monoresistant_state,
    To_state=mdr_state,
    Is_dynamic=True
))

# IHN to MDR
save(Transition_probability(
    From_state=inh_monoresistant_state,
    To_state=mdr_state,
    Is_dynamic=True
))

# MDR to XDR
save(Transition_probability(
    From_state=mdr_state,
    To_state=xdr_state,
    Is_dynamic=True
))


# We can now visualize this chain.

# In[310]:

link_tps_to_chains()
visualize_chain(tb_resistance_chain)
Image(filename='file.png')


# #TB treatment
# 
# Now, let's turn our attention to the TB treatment model. In addition to the uninfected state, we need to model three diseased states: untreated (latent), untreated (active) and treated. Let's create those states.

# In[311]:

# get TB treatment chain
tb_treatment_chain = Chain.query.filter_by(name="TB treatment").first()

# create the chains we need
state_names = ["Uninfected","Untreated - Latent", "Untreated - Active", "Treated"]

# save them with TB resistance chain
for state_name in state_names:
    the_state = State(name=state_name,chain=tb_treatment_chain)
    save(the_state)
    
# print chains from database
State.query.filter_by(chain=tb_treatment_chain).all()


# ##Raw inputs
# 
# Now let's look at the raw data.
# 
# Obviously, transition from uninfected to untreated latent and untreated latent to untreated active are dynamic.
# 
# Treatment uptake rates for active infections are not readily available. However, there is an estimated case detection of 62% (52–75).1 

# In[312]:

reference = Reference(name="WHO. Global tuberculosis report 2013. (2013)")

case_detection_rate = Raw_input(
    name="Estimated case detection",
    slug="case_detection_rate",
    value=0.62,
    low=0.52,
    high=0.75,
    reference=reference
)

save(case_detection_rate)


# One study of 376 confirmed active cases in South Africa suggested that only 74% of those diagnosed started treatment. I will assume that the high and low are 0.7 and 0.8
# 

# In[313]:

reference = Reference(name="Botha, E. et al. From suspect to patient...")

percent_diagnosed_treated = Raw_input(
    name="Proportion of diagnosed that recieve treatment",
    slug="percent_diagnosed_treated",
    value=0.74,
    low=0.7,
    high=0.8,
    reference=reference
)

save(percent_diagnosed_treated)


# Althougth this is not fully accurate, we can estimate the total percent of individuals who recieve treatment using these two values.

# In[314]:

overall_percent_active_treated = Raw_input(
    name="Percent of all active that will be treated",
    slug="overall_percent_active_treated",
    value=percent_diagnosed_treated.value * case_detection_rate.value,
    low=percent_diagnosed_treated.low * case_detection_rate.low,
    high=percent_diagnosed_treated.high * case_detection_rate.high,
)

save(overall_percent_active_treated)


# We will also assume that there is a drop-out rate of 10% (5-15%)

# In[315]:

drop_out_rate_annual = Raw_input(
    name="Annual drop out rate",
    slug="drop_out_rate_annual",
    value=0.1,
    low=0.05,
    high=0.15
)

save(drop_out_rate_annual)


# ##Transition probabilities
# 
# Now let's add in the transition probabilities.

# In[319]:

# convert annual to quarterly 

drop_out_rate_qt = convert_year_to_qt(drop_out_rate_annual.value)
enrollment_rate_qt = convert_year_to_qt(overall_percent_active_treated.value)


# get TB resistance chain
tb_treatment_chain = Chain.query.filter_by(name="TB treatment").first()

# Get states
uninfected_state=State.query.filter_by(name="Uninfected",chain=tb_treatment_chain).first()
untreated_latent_state=State.query.filter_by(name="Untreated - Latent",chain=tb_treatment_chain).first()
untreated_active_state=State.query.filter_by(name="Untreated - Active", chain=tb_treatment_chain).first()
treated_state=State.query.filter_by(name="Treated", chain=tb_treatment_chain).first()


# Uninfected to untreated latent
save(Transition_probability(
    From_state=uninfected_state,
    To_state=untreated_latent_state,
    Is_dynamic=True
))

# Untreated latent to untreated active
save(Transition_probability(
    From_state=untreated_latent_state,
    To_state=untreated_active_state,
    Is_dynamic=True
))


# Enrollment - Untreated active to treated active
save(Transition_probability(
    From_state=untreated_active_state,
    To_state=treated_state,
    Tp_base=enrollment_rate_qt
))


# Drop - out Untreated active to untreated active
save(Transition_probability(
    From_state=treated_state,
    To_state=untreated_active_state,
     Tp_base=drop_out_rate_qt
))




# Now, let's visualize this chain.

# In[320]:

link_tps_to_chains()
visualize_chain(tb_treatment_chain)
Image(filename='file.png')


# #HIV disease
# 
# Now, lets turn our attention to the HIV model. Let's start by building the disease model. Because the transition probabilites for infection are dynamic, we need to build some raw inputs.
# 
# Firstly, let's look at condom effectiveness. Let's assume a 0.9 to 1 low and high

# In[ ]:

condom = Raw_input(
    name="Percent of all active that will be treated",
    slug="overall_percent_active_treated",
    value=percent_diagnosed_treated.value * case_detection_rate.value,
    low=percent_diagnosed_treated.low * case_detection_rate.low,
    high=percent_diagnosed_treated.high * case_detection_rate.high,
)

save(overall_percent_active_treated)

