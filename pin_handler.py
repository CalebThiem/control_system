import threading


class PinHandler:

    '''
    
    Manages a list representing activated and deactivated relays. This list is sent to the 
    Arduino, which activates or deactivates each relay represented in the list. For details, 
    on how the Arduino receives and interprets the string, see Arduino.ino docstring. 

    Attributes:

        pin_array : list
            
            A list representing 96 relays

        excluded_list : list

            A list of relays that will be unaffercted by calls to setLeachRelays, 
            setElectrowinningRelays, and resetAll.

    Methods: 

        exludePins(list)

            Adds numbers in list parameter to excluded_list

        undoExcludePins(list)

            Removes numbers in list parameter from excluded_list

        setLeachRelays(list)

            For each number in list parameter, sets corresponding entry in pin_array[0:49]
            to 1, unless in excluded_list.

        setElectrowinnigRelays(list)

            For each number in list parameter, sets corresponding entry in pin_array[49:97] 
            to 1, unless in excluded_list.

        setRelayOn(list)

            For each number in list parameter, sets corresponding entry in pin_array to 1,
            across the entirety of pin_array.

        setRelaysOff(list)

            For each number in list parameter, sets corresponding entry in pin_array to 0,
            across the entirety of pin_array.

        resetAll()

            Sets entries in pin_array to 0, except for entries in excluded_list.

            
    '''

    def __init__(self):

        self.pin_array = []

        self.excluded_list = []

        self.lock = threading.Lock()

        for _ in range(48 * 2):

            self.pin_array.append("0")

    def pin_array_string(self):

        return "".join(self.pin_array)

    def excludePins(self, relayNumbers):

        print(f"excluded relays: {relayNumbers}")

        for i in relayNumbers:

            if i not in self.excluded_list:

                self.excluded_list.append(i)

        print(f"Exclude list: {self.excluded_list}")

    def undoExcludePins(self, relayNumbers):

        print(f"undid exclusion of relays {relayNumbers}")
        for i in relayNumbers:

            while i in self.excluded_list:

                self.excluded_list.remove(i)

    def setLeachRelays(self, relayNumbers):

        for i in range(49):

            if i not in self.excluded_list:

                self.pin_array[i - 1] = "0"

        for i in relayNumbers:

            if i not in self.excluded_list:

                self.pin_array[i - 1] = "1"

    def setElectrowinningRelays(self, relayNumbers):

        for i in range(49, 97):

            if i not in self.excluded_list:

                self.pin_array[i - 1] = "0"

        for i in relayNumbers:

            if i not in self.excluded_list:

                self.pin_array[i - 1] = "1"

    def setRelaysOn(self, relayNumbers):

        for i in relayNumbers:

            self.pin_array[i - 1] = "1"

    def setRelaysOff(self, relayNumbers):

        for i in relayNumbers:

            self.pin_array[i - 1] = "0"

    def resetAll(self):

        for i in range(len(self.pin_array)):

            if i+1 not in self.excluded_list:

                self.pin_array[i] = "0"
