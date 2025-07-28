from nicegui import ui, app
import asyncio
import json
import os

TIMEFRAMES = ['H1', 'D']
ASSETS = ['BTC', 'ETH', 'XRP', 'FARTCOIN']
INDICATORS = ['RSI', 'Simple MA', 'MACD', 'Boilinger Bands', 'Stocastic Oscilator', 'ATR']

bot_name_input = None
timeframe_select = None
assets_select = None
balance_input = None
risk_input = None
entry_conditions = []
take_profit_conditions = []
stop_loss_conditions = []


async def run_backtest():

    payload = {
        'bot': {},
        'entry': [],
        'take_profit': [],
        'stop_loss': [],
    }

    def extract_conditions(condition_list):
        result = []
        for item in condition_list:
            entry = {}
            indicator = item['dropdown'].value
            if not indicator:
                continue
            entry['indicator'] = indicator
            for k, v in item.items():
                if k in ['dropdown', 'fields', 'action_values_container']:
                    continue
                if hasattr(v, 'value'):
                    entry[k] = v.value
            if 'value' in item:
                entry['value'] = item['value'].value
            elif 'min_value' in item and 'max_value' in item:
                entry['min_value'] = item['min_value'].value
                entry['max_value'] = item['max_value'].value
            result.append(entry)
        return result

    payload['bot'] = {
        'name': bot_name_input.value,
        'timeframe': timeframe_select.value,
        'assets': assets_select.value,
        'account_balance': int(balance_input.value.replace('$', '').replace(',', '').strip()),
        'risk_percent': float(risk_input.value.replace('%', '').strip()),
    }
    payload['entry'] = extract_conditions(entry_conditions)
    payload['take_profit'] = extract_conditions(take_profit_conditions)
    payload['stop_loss'] = extract_conditions(stop_loss_conditions)

    print(payload)
    save_payload_to_file(payload)



def save_payload_to_file(payload, filename='payload.json'):
    os.makedirs('payloads', exist_ok=True)  
    filepath = os.path.join('payloads', filename)
    with open(filepath, 'w') as f:
        json.dump(payload, f, indent=4)
    print(f"Payload saved to {filepath}")



def add_fields(container, condition_list):
    with container:
        field = {}
        dropdown = ui.select(INDICATORS, multiple = False, label = "Select Indicator").classes('w-48 h-10')
        field['dropdown'] = dropdown
        field_container = ui.column()
        field['fields'] = field_container
        condition_list.append(field)

        def handle_change(e):
            field['fields'].clear()
            selected_indicator = e.args['label']
            match selected_indicator:
                case 'RSI':
                    with field['fields']:
                        with ui.row():
                            field['window'] = ui.number(label='Window', value=14, format='%1.0f')
                            field['source'] = ui.select(
                                ['Open', 
                                 'High', 
                                 'Low', 
                                 'Close'],
                                label='Source'
                            ).classes('w-48 h-10')

                            
                            action_dropdown = ui.select(
                                ['greater_than', 
                                'less_than', 
                                'in_range'],
                                label='Action On'
                            ).classes('w-48 h-10')
                            field['action'] = action_dropdown

                            
                            action_values_container = ui.row()
                            field['action_values'] = action_values_container

                            
                            def handle_action_change(e):
                                action_values_container.clear()

                                
                                for key in ['value', 'min_value', 'max_value']:
                                    if key in field:
                                        del field[key]

                                with action_values_container:
                                    action = e.value
                                    if action in ['greater_than', 'less_than']:
                                        field['value'] = ui.number(label='Value', format='%1.0f')
                                    elif action == 'in_range':
                                        field['min_value'] = ui.number(label='Min Value', format='%1.0f')
                                        field['max_value'] = ui.number(label='Max Value', format='%1.0f')
                            
                            action_dropdown.on_value_change(handle_action_change)

                
                case 'Simple MA':
                    with field['fields']:
                        with ui.row():
                            field['window'] = ui.number(label = 'Window', value = 9, format = "%1.0f")
                            field['source'] = ui.select(['Open', 
                                    'High', 
                                    'Low', 
                                    'Close'], multiple = False, label = "Source:").classes('w-48 h-10')
                            field['action'] = ui.select(['above_price', 
                                    'below_price', 
                                    'at_price', 
                                    'price_crossed_above', 
                                    'price_cross_below'], multiple = False, label = 'Action on:')
        
                case 'Boilinger Bands':
                    with field['fields']:
                        with ui.row():
                            field['window'] = ui.number(label = 'Window', value = 12, format = "%1.0f")
                            field['window_deviation'] = ui.number(label = "Window Deviation", value = 3, format = "%1.0f")
                            field['action'] = ui.select(['open_above_hband', 
                                    'open_below_lband', 
                                    'close_above_hband', 
                                    'close_below_lband', 
                                    'inside_lband', 
                                    'inside_hband', 
                                    'inside_bands' ], multiple = False, label = "Action On:").classes('w-48 h-10')
               
                case 'ATR':
                    with field['fields']:
                        with ui.row():
                            field['window'] = ui.number(label='Window', value=14, format='%1.0f')
                            field['source'] = ui.select(
                                ['Open', 
                                 'High', 
                                 'Low', 
                                 'Close'],
                                label='Source'
                            ).classes('w-48 h-10')

                            
                            action_dropdown = ui.select(
                                ['greater_than', 
                                'less_than', 
                                'in_range'],
                                label='Action On'
                            ).classes('w-48 h-10')
                            field['action'] = action_dropdown

                            
                            action_values_container = ui.row()
                            field['action_values'] = action_values_container

                            
                            def handle_action_change(e):
                                action_values_container.clear()

                                
                                for key in ['value', 'min_value', 'max_value']:
                                    if key in field:
                                        del field[key]

                                with action_values_container:
                                    action = e.value
                                    if action in ['greater_than', 'less_than']:
                                        field['value'] = ui.number(label='Value', format='%1.0f')
                                    elif action == 'in_range':
                                        field['min_value'] = ui.number(label='Min Value', format='%1.0f')
                                        field['max_value'] = ui.number(label='Max Value', format='%1.0f')
                            
                            action_dropdown.on_value_change(handle_action_change)
        dropdown.on('update:modelValue', handle_change)


@ui.page('/')
def start_page():


    with ui.grid().classes(
        'grid '
        'w-screen h-screen '
        'grid-cols-[3fr_2fr] auto-rows-auto '
        'gap-4 p-4'
    ):

        with ui.element().classes('col-start-1 row-start-1 row-span-6 overflow-auto h-full space-y-4'):
            with ui.card():
                ui.label('Entry Conditions')
                entry_container = ui.column().classes('w-full h-full')
                ui.button('Add Condition', on_click=lambda: add_fields(entry_container, entry_conditions)).classes('mt-2')

            with ui.card():
                ui.label('Take Profit Conditions')
                take_profit_container = ui.column().classes('w-full h-full')
                ui.button('Add Condition', on_click=lambda: add_fields(take_profit_container, take_profit_conditions)).classes('mt-2')

            with ui.card():
                ui.label('Stop Loss Conditions')
                stop_loss_container = ui.column().classes('w-full h-full')
                ui.button('Add Condition', on_click=lambda: add_fields(stop_loss_container, stop_loss_conditions)).classes('mt-2')

        with ui.card().classes('col-start-2 row-start-1 row-span-3'):
            global bot_name_input, timeframe_select, assets_select, balance_input, risk_input
            bot_name_input = ui.input(label="Bot name", value='Enter name').props('clearable')
            timeframe_select = ui.select(TIMEFRAMES, value=TIMEFRAMES[0], label="Timeframe:").classes('w-48 h-10')
            assets_select = ui.select(ASSETS, value=[], multiple=True, label="Assets:").classes('w-48 h-10')
            balance_input = ui.input(label="Account Balance", value='$10,000').props('clearable')
            risk_input = ui.input(label="Risk Percent", value='2%').props('clearable')

        with ui.card().classes('col-start-2 row-start-6 row-span-1'):
            ui.button("Run Backtest", on_click=run_backtest)

ui.run(host='0.0.0.0', port=8080, dark=True)




