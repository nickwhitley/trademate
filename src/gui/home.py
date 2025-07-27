from nicegui import ui
import asyncio

TIMEFRAMES = ['H1', 'D']
ASSETS = ['BTC', 'ETH', 'XRP', 'FARTCOIN']
INDICATORS = ['RSI', 'Simple MA', 'MACD', 'Boilinger Bands', 'Stocastic Oscilator', 'ATR']


async def run_backtest():
    n = ui.notification(timeout = None)
    for i in range(10):
        n.message = f'Running Backtest {i/10:.0%}'
        n.spinner = True
        await asyncio.sleep(0.2)
    n.message = "Backtest Complete"
    n.spinner = False
    await asyncio.sleep(1)
    n.dismiss()


@ui.page('/home')
def home_page():
    ui.label("Home page")
    ui.button('Go Back', on_click=lambda: ui.navigate('/'))

@ui.page('/results')
def results_page():
    ui.label("Results page")

@ui.page('/History')
def history_page():
    ui.label("History page")





def add_RSI():
    ui.number(label = 'Window', value = 14, format = "%1.0f")
    ui.select(['Open', 'High', 'Low', 'Close'], multiple = False, label = "Source:").classes('w-48 h-10')

def add_simple_ma():
    ui.number(label = 'Window', value = 9, format = "%1.0f")
    ui.select(['Open', 'High', 'Low', 'Close'], multiple = False, label = "Source:").classes('w-48 h-10')

def add_MACD():
    ui.number(label = 'Slow Window', value = 26, format = "%1.0f")
    ui.number(label = 'Fast Window', value = 12, format = "%1.0f")
    ui.number(label = 'Signal Window', value = 9, format = "%1.0f")

def add_boilinger():
    ui.number(label = 'Window', value = 12, format = "%1.0f")
    ui.number(label = "Window Deviation", value = 3, format = "%1.0f")

def add_stocastic_oscilator():
    ui.number(label = 'Window', value = 12, format = "%1.0f")
    ui.number(label = "Smoothed Window", value = 3, format = "%1.0f")

def add_ATR():
    ui.number(label = 'Window', value = 12, format = "%1.0f")

def add_fields(container):
    with container:
        dropdown = ui.select(INDICATORS, multiple = False, label='Select Indicator').classes('w-48 h-10')
        fields_container = ui.column()
        def handle_change(e):
            select_indicator(e.args['label'], fields_container)
        dropdown.on('update:modelValue', handle_change)

def select_indicator(selected_option, container):
    container.clear()
    # selected_option = event.value

    with container:
        match selected_option:
            case 'RSI':
                with ui.row():
                    add_RSI()
            case 'Simple MA':
                with ui.row():
                    add_simple_ma()
            case 'MACD':
                with ui.row():
                    add_MACD()
            case 'Boilinger Bands':
                with ui.row():
                    add_boilinger()
            case 'Stocastic Oscilator':
                with ui.row():
                    add_stocastic_oscilator()
            case 'ATR':
                with ui.row():
                    add_ATR()
    # fields_container.clear()

@ui.page('/')
def start_page():


    with ui.grid().classes(
        'grid '
        'w-screen h-screen '
        'grid-cols-[3fr_2fr] auto-rows-auto '
        'gap-4 p-4'
    ):
        # Scrollable Left Column
        with ui.element().classes('col-start-1 row-start-1 row-span-6 overflow-auto h-full space-y-4'):
            with ui.card():
                ui.label('Entry Conditions')
                entry_container = ui.column().classes('w-full h-full')
                ui.button('Add Condition', on_click=lambda: add_fields(entry_container)).classes('mt-2')

            with ui.card():
                ui.label('Take Profit Conditions')
                take_profit_container = ui.column().classes('w-full h-full')
                ui.button('Add Condition', on_click=lambda: add_fields(take_profit_container)).classes('mt-2')

            with ui.card():
                ui.label('Stop Loss Conditions')
                stop_loss_container = ui.column().classes('w-full h-full')
                ui.button('Add Condition', on_click=lambda: add_fields(stop_loss_container)).classes('mt-2')

        # Right Side - Bot Info
        with ui.card().classes('col-start-2 row-start-1 row-span-3'):
            ui.input(label="Bot name", value='Enter name').props('clearable')
            ui.select(TIMEFRAMES, multiple=False, label="Timeframe:").classes('w-48 h-10')
            ui.select(ASSETS, multiple=True, label="Assets:").classes('w-48 h-10')
            ui.input(label="Account Balance", value='$10,000').props('clearable')
            ui.input(label="Risk Percent", value='2%').props('clearable')

        with ui.card().classes('col-start-2 row-start-6 row-span-1'):
            ui.button("Run Backtest", on_click=run_backtest)

ui.run(title='dashboard layout')




