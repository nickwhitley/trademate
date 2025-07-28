import os
from data import data 
from nicegui import ui, app
from datetime import datetime
from gui.results import results_func  # or show_results, depending
from models.bot_config import BotConfig
from models.backtest_config import BacktestConfig
from models.trade_condition import TradeCondition
from models.condition_operator import Condition, ConditionOperator
from constants import Asset, Timeframe
from indicators.rsi import RSI
from indicators.simple_ma import MA
from indicators.bollinger_bands import BollingerBands
from indicators.atr import ATR
from backtesting.backtest import run_backtest as run_actual_backtest
from gui.shared_state import backtest_result_data
import asyncio
from asyncio import to_thread

TIMEFRAMES = ['H1', 'D']
ASSETS = ['BTC', 'ETH', 'XRP', 'FARTCOIN']
INDICATORS = ['RSI', 'Simple MA', 'Boilinger Bands', 'ATR']

selected_assets = []
bot_name_input = None
timeframe_select = None
assets_select = None
balance_input = None
risk_input = None
entry_conditions = []
take_profit_conditions = []
stop_loss_conditions = []
run_button = None
run_spinner_container = None


# async def run_backtest():
#     if not selected_assets:
#         ui.notify('Please select at least one asset before running the backtest.', color='negative')
#         return

#     if not selected_assets or all(not a.strip() for a in selected_assets):
#         ui.notify('Please select at least one asset before running the backtest.', color='negative')
#         return

#     if not entry_conditions:
#         ui.notify('Please add at least one Entry Condition.', color='negative')
#         return

#     if not take_profit_conditions:
#         ui.notify('Please add at least one Take Profit Condition.', color='negative')
#         return

#     if not stop_loss_conditions:
#         ui.notify('Please add at least one Stop Loss Condition.', color='negative')
#         return
    
#     payload = {
#         'bot': {},
#         'entry': [],
#         'take_profit': [],
#         'stop_loss': [],
#     }

#     def extract_conditions(condition_list):
#         result = []
#         for item in condition_list:
#             entry = {}
#             indicator = item['dropdown'].value
#             if not indicator:
#                 continue
#             entry['indicator'] = indicator
#             for k, v in item.items():
#                 if k in ['dropdown', 'fields', 'action_values_container']:
#                     continue
#                 if hasattr(v, 'value'):
#                     entry[k] = v.value
#             if 'value' in item:
#                 entry['value'] = item['value'].value
#             elif 'min_value' in item and 'max_value' in item:
#                 entry['min_value'] = item['min_value'].value
#                 entry['max_value'] = item['max_value'].value
#             result.append(entry)
#         return result

#     payload['bot'] = {
#         'name': bot_name_input.value,
#         'timeframe': timeframe_select.value,
#         'assets': assets_select.value or [],
#         'account_balance': int(balance_input.value.replace('$', '').replace(',', '').strip()),
#         'risk_percent': float(risk_input.value.replace('%', '').strip()),
#     }
#     payload['entry'] = extract_conditions(entry_conditions)
#     payload['take_profit'] = extract_conditions(take_profit_conditions)
#     payload['stop_loss'] = extract_conditions(stop_loss_conditions)

#     print(payload)
#     save_payload_to_file(payload)
def has_valid_conditions(conditions):
    for c in conditions:
        if not c.get('dropdown') or not c['dropdown'].value:
            continue
        if not c.get('action') or not c['action'].value:
            continue
        if 'value' in c and c['value'].value is None:
            continue
        if 'min_value' in c and 'max_value' in c:
            if c['min_value'].value is None or c['max_value'].value is None:
                continue
        return True  # Valid condition found
    return False  # None were valid

async def handle_run_backtest():
    run_button.props('loading=true disabled=true')
    run_spinner_container.visible = True

    try:
        # ✅ Validate user input
        if not selected_assets or all(not a.strip() for a in selected_assets):
            ui.notify('Please select at least one asset before running the backtest.', color='negative')
            return

        if not has_valid_conditions(entry_conditions):
            ui.notify('Please add at least one valid Entry Condition.', color='negative')
            return

        # ✅ Convert UI values to enum/model instances
        enum_assets = [getattr(Asset, asset + "_USD") for asset in selected_assets]
        timeframe_enum = getattr(Timeframe, timeframe_select.value)

        def to_trade_conditions(conditions):
            result = []
            for c in conditions:
                indicator_name = c['dropdown'].value
                if not indicator_name:
                    continue

                match indicator_name:
                    case 'RSI': indicator = RSI()
                    case 'Simple MA': indicator = MA()
                    case 'Boilinger Bands': indicator = BollingerBands()
                    case 'ATR': indicator = ATR()
                    case _: continue

                action = c.get('action')
                if not action or not action.value:
                    continue

                op = getattr(ConditionOperator, action.value)

                if 'value' in c and c['value'].value is not None:
                    cond = Condition(operator=op, value=c['value'].value)
                elif 'min_value' in c and 'max_value' in c:
                    min_val = c['min_value'].value
                    max_val = c['max_value'].value
                    if min_val is not None and max_val is not None:
                        cond = Condition(operator=op, range=(min_val, max_val))
                    else:
                        continue
                else:
                    cond = Condition(operator=op)

                result.append(TradeCondition(indicator=indicator, condition=cond))
            return result

        entry_conds = to_trade_conditions(entry_conditions)
        take_profit_conds = to_trade_conditions(take_profit_conditions)
        stop_loss_conds = to_trade_conditions(stop_loss_conditions)

        bot_config = BotConfig(
            bot_name=bot_name_input.value,
            assets=enum_assets,
            timeframe=timeframe_enum,
            entry_conditions=entry_conds,
            exit_conditions=take_profit_conds + stop_loss_conds,
            order_size_usd=int(balance_input.value.replace('$', '').replace(',', '')),
        )

        backtest_config = BacktestConfig(
            start_date=datetime(2023, 1, 1),
            end_date=datetime.now(),
            starting_balance=int(balance_input.value.replace('$', '').replace(',', '')),
        )

        # ✅ Background task to avoid blocking UI
        async def background_job():
            try:
                os.makedirs('./src/data/parquet/', exist_ok=True)

                for asset in enum_assets:
                    print(f"Fetching data for: {asset.name} / {timeframe_enum.name}")
                    df = await to_thread(data.get_df, asset=asset, timeframe=timeframe_enum)
                    print(f"Loaded {len(df)} rows for {asset.name}")

                result = await to_thread(run_actual_backtest, bot_config, backtest_config)

                backtest_result_data['config'] = bot_config
                backtest_result_data['result'] = result

                ui.run_javascript("window.location.href = '/results-dynamic'")
            except Exception as e:
                import traceback
                traceback.print_exc()
                escaped = str(e).replace('"', '\\"')
                ui.run_javascript(f'window.alert("Backtest error: {escaped}")')
            finally:
                run_button.props('loading=false disabled=false')
                run_spinner_container.visible = False

        ui.timer(0.1, background_job, once=True)

    except Exception as e:
        import traceback
        traceback.print_exc()
        ui.notify(f'Backtest error: {e}', color='negative')
        run_button.props('loading=false disabled=false')
        run_spinner_container.visible = False


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
            for key in list(field.keys()):
                if key not in ['dropdown', 'fields']:
                    del field[key]
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
                                    'price_crossed_below'], multiple = False, label = 'Action on:')
        
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
    global assets_select
    global selected_assets, entry_conditions, take_profit_conditions, stop_loss_conditions
    entry_conditions = []
    take_profit_conditions = []
    stop_loss_conditions = []
    selected_assets = []

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
            def update_assets(e):
                global selected_assets
                selected_assets = e.value or []
                print('Selected assets updated:', selected_assets)

            assets_select.on_value_change(update_assets)

        with ui.card().classes('col-start-2 row-start-6 row-span-1'):
            global run_button, run_spinner, run_spinner_container  # ✅ FIXED LINE
            run_button = ui.button("Run Backtest", on_click=handle_run_backtest)

            with ui.row().classes('items-center') as run_spinner_container:
                run_spinner = ui.spinner(size='lg').props('color=primary')
            run_spinner_container.visible = False
            ui.link('go to results','/results_dynamic')

ui.run(host='0.0.0.0', port=8080, dark=True)








