import time
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template
import random

########## This function to do comparison for the RandWalker  ################# 
def func_contraint(min_val, max_val, contraint_value):
    value = random.randint(min_val, max_val)
    while value < contraint_value :
        value = random.randint(min_val, max_val)
    return value

###############      RandomWalker           ###############
    

class RandomWalker(Agent):
    class MyBehav(CyclicBehaviour):
        async def on_start(self):
            print("Starting behaviour . . . RandomWalker")
            self.history = []
            #Range of generated values
            self.min_value = 0 
            self.max_value = 3000
            
            ########
            self.players = ["carefulAgent@jabber.lqdn.fr"]
            self.value = random.randint(self.min_value, self.max_value)
            self.history.append(self.value)

        async def run(self):
            print("RecvBehav running  [   RandomWalker   ]")
            #################### Sent the random value to the CarefulAgent the others ####################           
            for player in self.players:
                msg = Message(to=player)  # Instantiate the message
                msg.set_metadata(
                    "performative", "inform"
                )  # Set the "inform" FIPA performative
                print("message sent to ------> "+player)
                msg.body = str(self.value)  # Set the message content
                await self.send(msg)

            #################### receive messages from agents   ####################

            msg_rec = await self.receive(
                timeout=20
            )  # wait for a message for 20 seconds

            # sent process
            if msg_rec:
                reci_value = int(msg_rec.body)
                self.value = random.randint(self.min_value, self.max_value)
                
                self.history.append(self.value)
            else:
                print(
                    "Did not received any message after 20 seconds [[ Message from agent juge ]]"
                )

        # at the and of the behaviour
        async def on_end(self):
            pass

    async def setup(self):
        print("Agent starting . . . RandomWalker")
        b = self.MyBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)

###############      CarefulAgent           ###############
        
        
        
class CarefulAgent(Agent):
    class InformJuge(CyclicBehaviour):
        async def on_start(self):
            self.randomWalker = "randomWalker@jabber.lqdn.fr"
            pass

        async def run(self):
            ##################  recive the value from the RandomWlaker   ##################
            print("RecvBehav running [  CarefulAgent  ]")
            msg = await self.receive(timeout=20)
            # we use str() to convert the type of msg.sender
            print(msg)
            if msg and str(msg.sender) == self.randomWalker:
                if msg.body :
                    value = int(msg.body)
                    random_value = random.randint(0, value)
                    ####### sent the value ################
                    msg = Message(to= self.randomWalker)  # Instantiate the message
                    msg.set_metadata(
                        "performative", "inform"
                    )  # Set the "inform" FIPA performative
                    msg.body = str(random_value)  # Set the message content
                    await self.send(msg)
                    
            else:
                print(
                    "Did not received any message after 20 seconds [[ Message from agent CarefulAgent ]]"
                )

    async def setup(self):
        # print("Sender Agent started")
        b = self.InformJuge()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)


if __name__ == "__main__":

    carefulAgent = CarefulAgent("carefulAgent@jabber.lqdn.fr", "1234567890")
    randomWalker = RandomWalker("randomWalker@jabber.lqdn.fr", "1234567890")
    future = carefulAgent.start()
    future.result() # wait for receiver agent to be prepared.
    future = randomWalker.start()
    future.result() # wait for receiver agent to be prepared.


    while randomWalker.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            randomWalker.stop()
            carefulAgent.stop()
            break
    print("Agents finished")
