from importlib import import_module, reload


streamlitAppModule = import_module("rag_budget.presentation.streamlit_app")
streamlitAppModule = reload(streamlitAppModule)
streamlitAppModule.renderPage()
