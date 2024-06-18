import threading


class PinHandler:

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
