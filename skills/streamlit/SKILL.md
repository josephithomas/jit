---
name: streamlit
description: "Rapid prototyping of data science apps, interactive dashboards, and ML demos using Streamlit."
license: MIT
source: https://github.com/streamlit/streamlit
---

# Streamlit App Engineering

Interactive dashboards and ML prototypes.

## Best Practices
- **Caching**: Decorate expensive calculations and data loading with `@st.cache_data` or `@st.cache_resource`.
- **Session State**: Preserve user inputs and pagination across script re-runs using `st.session_state`.
- **Layout**: Organize content logically with `st.columns`, `st.tabs`, and `st.sidebar`.
