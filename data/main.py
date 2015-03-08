from . import prepare,tools
from .states import aquarium_screen

def main():
    controller = tools.Control()
    states = {"AQUARIUM": aquarium_screen.Aquarium()}
    controller.setup_states(states, "AQUARIUM")
    controller.main()
