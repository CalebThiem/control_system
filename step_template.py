def step_1(self, mode):


    self.current_thread = self.step_1

    # Define the text that will be displayed when the step is selected

    text_as_list = [
            "step text",
            "more step text"
        ]

    # Call the function that updates the text on the GUI

    self.write_steps_display_text(text_as_list)

    if (mode == "run_logic"):

        self.step_running = True

        start_time = time.time()

        while self.step_running:

            # Check alarm conditions

            if alarm_conditons:

                self.cancel() # Changes step_running to False, other things

                self.raise_alarm()

                break

            # Check step progression conditions

            if step_conditions:

                self.step_running = False

                self.load_next_step()

                self.call_current_thread()

                break



            

