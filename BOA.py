import time
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template
import random
import asyncio

########## This function to do comparison for the RandWalker  ################# 
def func_contraint(min_val, max_val, contraint_value):
    value = random.randint(min_val, max_val)
    while value < contraint_value :
        value = random.randint(min_val, max_val)
    return value


###############      RandomWalker           ###############
    

class RandomWalker(Agent):
    class MyBehav(CyclicBehaviour):
        ##send messages to alist of agents
        async def notifiy_pub(self, players, body):#body str
            for player in self.players:
                msg = Message(to=player)  # Instantiate the message
                msg.set_metadata(
                    "performative", "inform"
                )  # Set the "inform" FIPA performative
                #print("message sent to ------> "+player)
                msg.body = body  # Set the message content
                await self.send(msg)
        
        async def on_start(self):
            print("RandomWalker: Bonjour ! ! \n")
            self.history = []
            #Range of generated values
            self.min_value = 0 
            self.max_value = 3000
            
            self.players = ["carefulAgent@jabber.lqdn.fr"]
            self.value = random.randint(self.min_value, self.max_value)
            self.history.append(self.value)
            #################### Sent the random value to the CarefulAgent the others ####################           
            await self.notifiy_pub(self.players, str(self.value))

        async def run(self):
            #print("RecvBehav running  [   RandomWalker   ]")
            #################### receive messages from agents   ####################

            msg_rec = await self.receive(
                timeout=20
            )  # wait for a message for 20 seconds

            # sent process
            if msg_rec:
                reci_value = int(msg_rec.body)
                self.value = func_contraint(self.min_value, self.max_value, reci_value)
                print("RandomWalker : c'est trop petite :"+str(reci_value))
                print("RandomWalker : vous allez me donner :"+str(self.value)+"\n")
                await asyncio.sleep(10)# wait 10 seconds
                await self.notifiy_pub(self.players, str(self.value))
                
            else:
                print(
                    "Did not received any message after 20 seconds [[ Message from agent RandomWalker ]]"
                )
                await self.notifiy_pub(self.players, str(self.value))

        # at the and of the behaviour
        async def on_end(self):
            pass

    async def setup(self):
        #print("Agent starting . . . RandomWalker")
        b = self.MyBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)


###############      CarefulAgent           ###############
             
        
class CarefulAgent(Agent):
    class MyBeha(CyclicBehaviour):
        async def on_start(self):
            self.randomWalker = "randomwalker@jabber.lqdn.fr"
            print("CarefulAgent: Bonjour *_* \n")
            pass

        async def run(self):
            ##################  recive the value from the RandomWlaker   ##################
            #print("RecvBehav running [  CarefulAgent  ]")
            msg = await self.receive(timeout=20)
            # we use str() to convert the type of msg.sender
            if msg and str(msg.sender) == self.randomWalker:
                value = int(msg.body)
                print("CarefulAgent : c'est trop :"+str(value))
                random_value = random.randint(0, value)
                print("CarefulAgent : je vais vous donner :"+str(random_value)+"\n")
                ####### sent the value ################
                msg = Message(to= self.randomWalker)  # Instantiate the message
                msg.set_metadata(
                    "performative", "inform"
                )  # Set the "inform" FIPA performative
                msg.body = str(random_value)  # Set the message content
                await asyncio.sleep(10) # wait 10 seconds
                await self.send(msg)
                    
            else:
                print(
                    "Did not received any message after 20 seconds [[ Message from agent CarefulAgent ]]"
                )

    async def setup(self):
        # print("Sender Agent started")
        b = self.MyBeha()
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
