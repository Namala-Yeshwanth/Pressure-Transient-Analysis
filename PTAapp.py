import streamlit as st
import pandas as pd
import numpy as np
import math 
import matplotlib.pyplot as plt

# Step 1: Allow user to upload an Excel file
st.title("Pressure transient Analysis")

mu = st.sidebar.number_input("Viscosity(cp)", min_value=0.00, max_value=30.00, value=0.8)
Q = st.sidebar.number_input("Flow rate(stb/day)", min_value=10, max_value=600, value=500)
rw = st.sidebar.number_input('Wellbore Radius (ft)', min_value=0.00, max_value=10.00, value=0.2)
pi = st.sidebar.number_input('Initial Reservoir Pressure(psi)', min_value=100, max_value=10000, value=6102)
B = st.sidebar.number_input('Formation Volume Factor(bbl/stb)', min_value=0.01, max_value=2.00, value=1.13)
h = st.sidebar.number_input('formation thickness(feet)', min_value=2, max_value=500, value=70)
poro = st.sidebar.number_input('Porosity', min_value=0.00, max_value=1.00, value=0.10)
c = st.sidebar.number_input('Compressibility(psi)', min_value=0.00, max_value=1.00, value=17*pow(10,-6), step=0.0000001, format="%.7f")


uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])



# Checkbox to display data
if uploaded_file:
    show_data = st.checkbox("Show Data")

    # Read the Excel file
    try:
        data = pd.read_excel(uploaded_file)
        
        # Display data if checkbox is selected
        if show_data:
            st.write("Uploaded Data:")
            st.dataframe(data)
    except Exception as e:
        st.error(f"Error reading the file: {e}")

else:
    pdf = st.checkbox("Give result on sample data")
    if pdf:
        # Step 2: Read the uploaded Excel file into a DataFrame
        df = pd.read_excel('Oil_Well_Drawdown_Test_Question.xlsx')
        
        df1 = df

        # Step 3: Display the data
        st.write("Data from the uploaded file:")
        st.dataframe(df)


        # Step 4: Select columns for plotting
        columns = df.columns.tolist()
        x_column = st.selectbox("Select X-axis column", columns)
        y_column = st.selectbox("Select Y-axis column", columns)

    # Step 5: Plot the data
        if st.button("Generate Linear Plot", key="linear_plot"):
            plt.style.use('_classic_test_patch')
            plt.figure(figsize=(10,6))
            fig, ax = plt.subplots()
            ax.plot(df[x_column], df[y_column],linewidth=2)
            ax.grid(True)
            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)
            ax.set_title(f'{y_column} vs {x_column}')
            st.pyplot(fig)
        
        st.subheader("Transient Flow curve at constant flow rate")
        if st.button("Generate SemiLog-Plot", key="semilog_plot"):


            plt.style.use('_classic_test_patch')
        
            fig, ax = plt.subplots()
            ax.semilogx(df[x_column], df[y_column],linewidth=2)  # X-axis on a logarithmic scale
            ax.grid(True)
            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)
            ax.set_title(f'{y_column} vs {x_column} (Semi-Logarithmic Plot)')
            st.pyplot(fig)

            st.write(''' - This curve shows after a sufficient time Pressure vary linearly with logrithmic of time.
                            The region is know as infinite acting radial flow(IARF).''')
        st.subheader('For selection the time period the slicer will be given below')
        if 'start_row' not in st.session_state:
            st.session_state.start_row = 0
        if 'end_row' not in st.session_state:
                st.session_state.end_row = df.shape[0] - 1

        # Select range of rows to plot
        start_row = st.slider("Select start row", 0, df.shape[0] - 1, st.session_state.start_row, key="start_row_slider")
        end_row = st.slider("Select end row", 0, df.shape[0] - 1, st.session_state.end_row, key="end_row_slider")

        # Update session state with slider values
        st.session_state.start_row = start_row
        st.session_state.end_row = end_row
        
        st.subheader("Estimation of Permeability and Skin")
        st.write('Note: For estimation permeability and skin select the proper IARF region using slicer')
        # Generate Plot
        if st.button("Generate IARF region Plot", key="filtered_plot"):
            if start_row >= end_row:
                st.warning("Start row must be less than end row.")
            else:
                # Filter DataFrame based on selected row range
                df_filtered = df.iloc[start_row:end_row+1]
                plt.style.use('_classic_test_patch')
                
                fig, ax = plt.subplots()
                ax.semilogx(df_filtered[x_column], df_filtered[y_column],linewidth=2)
                ax.grid(True)
                
                
                ax.set_xlabel(x_column)
                ax.set_ylabel(y_column)
                ax.set_title(f'{y_column} vs {x_column}(Semi-Logarithmic Plot)')
                st.pyplot(fig)
                
                # Assuming df[x_column] and df[y_column] are the data used for plotting
                x = df_filtered[x_column]
                y = df_filtered[y_column]

    # Perform linear regression (1st degree polynomial)
                slope, intercept = np.polyfit(x, y, 1)

    # Print the equation of the line
                st.write(f"Equation of the line: y = {slope:.2f}x + {intercept:.2f}")
                
                i = intercept
                m = -slope 
                st.write(''' - So by equating slope with 162.6𝑄𝜇𝐵/kh and get the value of Permeability(k)''')
                st.write('''- And for skin estimation S = 1.15*(((pi - i)/m )- (log(k/(Φ * μ * c * (rw)^2))) +3.23)
                        ''')
                k = (162.6*Q*mu*B)/ (m*h)

                S = 1.15*(((pi - i)/m )- (math.log(k/(poro*mu*c*pow(rw,2)))) +3.23)


                
                st.write(
                pd.DataFrame(
            {
                "Parameter": ["Absolute Permeability","Skin","Slope"],
                "Value ": [k,S,m],           
            }
        )        
    )   
        st.subheader("Wellbore Storage")        
        st.write("- Wellbore storage refers to the initial phase when production comes from fluid expansion in the wellbore, not the reservoir.")         
        st.write('Note: For estimation wellbore constant select the proper wellbore region using slicer')
        # Generate Plot
        if st.button("Generate WellBore Storage region Plot", key="filtered_plot_1"):
            if start_row >= end_row:
                st.warning("Start row must be less than end row.")
            else:
                # Filter DataFrame based on selected row range
                df_filtered_1 = df.iloc[start_row:end_row+1]
                plt.style.use('_classic_test_patch')
                plt.figure(figsize=(10,6))
                fig, ax = plt.subplots()
                ax.plot(df_filtered_1[x_column], df_filtered_1[y_column],linewidth=2)
                ax.grid(True)
                ax.set_xlabel(x_column)
                ax.set_ylabel(y_column)
                ax.set_title(f'{y_column} vs {x_column}(Semi-Logarithmic Plot)')
                st.pyplot(fig)
                
                # Assuming df[x_column] and df[y_column] are the data used for plotting
                x1 = df_filtered_1[x_column]
                y1 = df_filtered_1[y_column]

    # Perform linear regression (1st degree polynomial)
                slope, intercept = np.polyfit(x1, y1, 1)

    # Print the equation of the line
                st.write(f"Equation of the line: y = {slope:.2f}x + {intercept:.2f}") 

                st.markdown("For estimation of Wellbore Constant") 
                st.write("C = (Q*B)/ (m*24)")

                i = intercept
                m = -slope 
                C = (Q*B)/ (m*24)                   
                st.write(
                pd.DataFrame(
            {
                "Parameter": ["Well bore Storage Constant"],
                "Value ": [C],           
            }
        )        
    )     
                


        st.subheader("Pressure derivative Plot")
        
        if st.button("Generate Derivative Log-Plot", key="log_plot"):

            df1['delta P_dash'] = np.nan

            df1['time'] = np.nan

            df1['delta P'] = np.nan


    # Calculate (C2-C1)/(T2-T1) for rows 1 to end, and assign to the new column
            df1['delta P_dash'].iloc[1:] = ((-df1.iloc[1:, 0])* (df1.iloc[1:, 1].values - df1.iloc[:-1, 1].values) / (df1.iloc[1:, 0].values - df1.iloc[:-1, 0].values))
        
            df1['time'].iloc[0:] =  (df1.iloc[0:, 0].values )
            df1['delta P'].iloc[1:] =  -1*(df1.iloc[1:, 1].values - df1.iloc[0, 1])

            st.write('''- Values of ΔP , t , P' are there:''')
            st.write('ΔP = Pi - P')
            st.write('''P' = dP / d(ln(t))''')
            st.dataframe(df)

            plt.style.use('_classic_test_patch')
            #plt.figure(figsize=(10,6))
            y_col1 = 'delta P_dash'
            x_col = 'time'
            y_col2 = 'delta P'
            fig, ax = plt.subplots()

    # Plot the first graph (delta P_dash vs delta t) with log-log scale
            ax.loglog(df[x_col], df[y_col1], linewidth=2, label=f'''P' vs t''')
            ax.grid(True)

    # Plot the second graph (P vs delta t) on the same axes
            ax.plot(df[x_col], df[y_col2], linewidth=2, color='orange', label=f'ΔP vs t')

    # Set axis labels
            ax.set_xlabel('t')
            ax.set_ylabel(f'''ΔP and P' ''')

    # Add a title and legend
            ax.set_title(f'''ΔP and P' vs Δt''')
            ax.legend()         
            st.pyplot(fig)

            st.write(" - For conventional plot we do not able to get minute details like where does wellbore storage over, where does radial flow starts etc.")
            st.markdown('''This Problem solve by derevative Plot''')

            st.write(" -  Information get from derevative Plot are")
            st.markdown("In initial phase slope of ΔP and P' is same it refers to wellbore storage")
            st.markdown("When slope of ΔP becomes 0 it refers to radial flow")

        

        
        A = st.number_input("Enter the value of a:", value=135.0)
        b = st.number_input("Enter the value of b:", value=0.0)

        if st.button("Estimation of K and S using derevative method"):
            df1['delta P_dash'] = np.nan

            df1['time'] = np.nan

            df1['delta P'] = np.nan


            df1['delta P_dash'].iloc[1:] = ((-df1.iloc[1:, 0])* (df1.iloc[1:, 1].values - df1.iloc[:-1, 1].values) / (df1.iloc[1:, 0].values - df1.iloc[:-1, 0].values))
        
            df1['time'].iloc[0:] =  (df1.iloc[0:, 0].values )
            df1['delta P'].iloc[1:] =  -1*(df1.iloc[1:, 1].values - df1.iloc[0, 1])




            plt.style.use('_classic_test_patch')
            #plt.figure(figsize=(10,6))
            y_col1 = 'delta P_dash'
            x_col = 'time'
            y_col2 = 'delta P'
            fig, ax = plt.subplots()

        # Plot the first graph (delta P_dash vs delta t) with log-log scale
            ax.loglog(df[x_col], df[y_col1], linewidth=2, label=f'''P' vs t''')
            ax.grid(True)

        # Plot the second graph (P vs delta t) on the same axes
            ax.plot(df[x_col], df[y_col2], linewidth=2, color='orange', label=f'ΔP vs t')

            ax.loglog(df1[x_col], A *(df1[x_col] ** b) , linewidth=2,  linestyle='--', color='black', label=f'y = {A}x + {b}')
    
        # Set axis labels
            ax.set_xlabel('t')
            ax.set_ylabel(f'''ΔP and P' ''')

        # Add a title and legend
            ax.set_title(f'''ΔP and P' vs Δt''')
            ax.legend()         
            st.pyplot(fig)


    # Perform linear regression (1st degree polynomial)
            slope, intercept = np.polyfit(df1[x_col], A *(df1[x_col] ** b), 1)

    # Print the equation of the line
            st.write(f"Equation of the line: y = {slope:.2f}x + {intercept:.2f}")
            
            i = intercept
            m = 2.303*i 
            st.write(''' - So by equating slope with 70.6𝑄𝜇𝐵/P'h and get the value of Permeability(k)''')
            st.write('''- And for skin estimation S = 1.15*(((pi - i)/m )- (log(k/(Φ * μ * c * (rw)^2))) +3.23)
                        ''')
            k = (70.6*Q*mu*B)/ (i*h)

            S = 1.15*(((pi - i)/m )- (math.log(k/(poro*mu*c*pow(rw,2)))) +3.23)


            
            st.write(
            pd.DataFrame(
        {
            "Parameter": ["Absolute Permeability","Skin","Slope"],
            "Value ": [k,S,m],           
        }
    )        
    )  

            

    st.subheader("Some sample dataset")
    # Replace this with your actual Google Drive shareable link
    drive_link = "https://docs.google.com/spreadsheets/d/1vHm-s_8o8-_6qhOP7eHfJvwXkjz516zp/edit?usp=sharing&ouid=104979325949300463767&rtpof=true&sd=true"
    # Create a download button or clickable link
    st.markdown(f"[Download Sample Excel file]( {drive_link} )")

            
                
        
        