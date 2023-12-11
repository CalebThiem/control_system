from nicegui import ui

# Event handler to update various elements
def on_update():
    # Update text and markdown contents
    text_label.set_text('Updated Text')
    markdown_content.set_markdown('**Updated Markdown**')

    # Update button text
    update_button.set_text('Clicked!')

    # Update input field values
    text_input.set_value('New Text')
    number_input.set_value(42)

    # Update image source (ensure you have a valid image path or URL)
    image.set_source('/path/to/new/image.png')

    # Update list options
    select.set_options(['Option 3', 'Option 4'])
    radio_group.set_options(['Radio 3', 'Radio 4'])

    # Update table data
    table.set_data([['Row 3', 'Data 3'], ['Row 4', 'Data 4']])

    # Update slider value
    slider.set_value(75)

# UI Elements
text_label = ui.label('Initial Text')
markdown_content = ui.markdown('**Initial Markdown**')
update_button = ui.button('Update', on_click=on_update)
text_input = ui.input('Initial Text')  # Corrected here
image = ui.image('/path/to/initial/image.png')  # Ensure valid path
select = ui.select(['Option 1', 'Option 2'])
radio_group = ui.radio_group(['Radio 1', 'Radio 2'])
table = ui.table([['Row 1', 'Data 1'], ['Row 2', 'Data 2']])
slider = ui.slider(min=0, max=100, value=50)

ui.run()
