"""Example of using AgenticGPT's memory abilities."""
from agentic_gpt.agent import AgenticGPT
from agentic_gpt.agent.action import Action

DOCUMENTS = {
    "capybara": "The capybara[a] or greater capybara (Hydrochoerus hydrochaeris) is a giant cavy rodent native to South America. It is the largest living rodent[2] and a member of the genus Hydrochoerus. The only other extant member is the lesser capybara (Hydrochoerus isthmius). Its close relatives include guinea pigs and rock cavies, and it is more distantly related to the agouti, the chinchilla, and the nutria. The capybara inhabits savannas and dense forests, and lives near bodies of water. It is a highly social species and can be found in groups as large as 100 individuals, but usually live in groups of 10–20 individuals. The capybara is hunted for its meat and hide and also for grease from its thick fatty skin.[3] It is not considered a threatened species.",
    "goose": "A goose (pl: geese) is a bird of any of several waterfowl species in the family Anatidae. This group comprises the genera Anser (the grey geese and white geese) and Branta (the black geese). Some other birds, mostly related to the shelducks, have \"goose\" as part of their names. More distantly related members of the family Anatidae are swans, most of which are larger than true geese, and ducks, which are smaller."
}


if __name__ == "__main__":
    agent = AgenticGPT(
        "What is a capybara? Print out the answer.",
        actions_available=[
            Action(
                name="speak",
                description="Speak the given text.",
                function=lambda text: print(text),
            )
        ],
        memory_dict=DOCUMENTS,
    )
    agent.run()
    # agent.save_actions_taken("examples/memory_example_actions_taken.json")
