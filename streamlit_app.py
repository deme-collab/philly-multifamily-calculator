import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO

# Import our calculator functions
from calculator import (
    analyze_multifamily_property, 
    get_client_friendly_neighborhood,
    format_results_as_string,
    ZIP_TO_GROUP_MAPPING,
    GROUP_TO_RENT_TYPE,
    PAYMENT_STANDARDS
)

# PDF generation with ReportLab
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfgen import canvas
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Philadelphia Multifamily Analyzer",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #f0f2f6;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def generate_pdf_report(analysis_results, input_params, property_address="N/A", property_notes="N/A"):
    """Generate PDF report from analysis results using ReportLab."""
    if not PDF_AVAILABLE:
        return None, "PDF generation not available. Please install reportlab."
    
    try:
        # Format the results as text
        results_text = format_results_as_string(analysis_results, input_params)
        
        # Create PDF buffer
        pdf_buffer = BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor='#333333',
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor='#444444',
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor='#000000',
            spaceAfter=6,
            fontName='Helvetica'
        )
        
        code_style = ParagraphStyle(
            'CustomCode',
            parent=styles['Code'],
            fontSize=9,
            textColor='#000000',
            fontName='Courier',
            leftIndent=20,
            spaceAfter=4
        )
        
        # Title
        elements.append(Paragraph("Philadelphia Multifamily Property Analysis Report", title_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Date
        date_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        elements.append(Paragraph(date_text, normal_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Property Information Section
        elements.append(Paragraph("Property Information", heading_style))
        elements.append(Paragraph(f"<b>Address:</b> {property_address}", normal_style))
        elements.append(Paragraph(f"<b>ZIP Code:</b> {input_params['property_zip_code']}", normal_style))
        elements.append(Paragraph(f"<b>Neighborhood:</b> {get_client_friendly_neighborhood(input_params['property_zip_code'])}", normal_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Analysis Notes Section
        if property_notes and property_notes.strip() and property_notes != "N/A":
            elements.append(Paragraph("Analysis Notes", heading_style))
            # Split notes into lines and add each as a paragraph
            for line in property_notes.split('\n'):
                if line.strip():
                    elements.append(Paragraph(line, normal_style))
            elements.append(Spacer(1, 0.2*inch))
        
        # Financial Analysis Section
        elements.append(Paragraph("Financial Analysis Details", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Split the results text into lines and format as monospace
        for line in results_text.split('\n'):
            # Escape special characters for XML
            line_escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            # Replace spaces with non-breaking spaces to preserve formatting
            line_escaped = line_escaped.replace(' ', '&nbsp;')
            elements.append(Paragraph(f"<font name='Courier' size='8'>{line_escaped}</font>", normal_style))
        
        # Build PDF
        doc.build(elements)
        
        # Get the PDF data
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue(), None
        
    except Exception as e:
        return None, f"PDF generation error: {str(e)}"

def create_charts(analysis_results):
    """Create visualization charts for the analysis."""
    summary = analysis_results.get('property_summary', {})
    
    if summary.get('error'):
        return None
    
    # Create enhanced Sankey diagram for cash flow with NOI layer
    monthly_rent = summary.get('total_potential_pha_rent_monthly', 0)
    monthly_vacancy = summary.get('vacancy_allowance_annual', 0) / 12
    effective_gross_income = monthly_rent - monthly_vacancy
    
    # Operating expenses (before debt service)
    monthly_taxes = summary.get('monthly_taxes', 0)
    monthly_insurance = summary.get('monthly_insurance', 0)
    monthly_repairs = summary.get('repairs_allowance_annual', 0) / 12
    monthly_management = summary.get('management_fee_annual', 0) / 12
    monthly_other = summary.get('other_opex_annual_input', 0) / 12
    
    # NOI and debt service
    monthly_noi = summary.get('noi_annual', 0) / 12
    monthly_pi = summary.get('monthly_principal_interest', 0)
    monthly_cash_flow = summary.get('cash_flow_before_tax_monthly', 0)
    
    # Total operating expenses
    total_operating_expenses = monthly_taxes + monthly_insurance + monthly_repairs + monthly_management + monthly_other
    
    # Restructured nodes with optimized positioning
    labels = [
        "Gross Rent",               # 0
        "Effective Income",         # 1
        "Vacancy Loss",             # 2 - Bottom branch
        "Operating Costs",          # 3 - Bottom section
        "NOI",                      # 4 - Top section
        "Property Tax",             # 5 - Bottom row
        "Insurance",                # 6 - Bottom row
        "Repairs",                  # 7 - Bottom row
        "Management",               # 8 - Bottom row
        "Other Costs",              # 9 - Bottom row
        "Debt Service",             # 10 - Middle
        "Net Cash Flow"             # 11 - Top position
    ]
    
    # Define connections
    source = []
    target = []
    value = []
    
    # Stage 1: Gross Rent flows
    if monthly_rent > 0:
        # Main flow: Gross Rent → Effective Income
        source.append(0)  # Gross Rent
        target.append(1)  # Effective Income
        value.append(effective_gross_income)
        
        # Separate branch: Gross Rent → Vacancy Loss (if exists)
        if monthly_vacancy > 0:
            source.append(0)  # Gross Rent
            target.append(2)  # Vacancy Loss
            value.append(monthly_vacancy)
    
    # Stage 2: Effective Income splits
    if effective_gross_income > 0:
        if total_operating_expenses > 0:
            source.append(1)  # Effective Income
            target.append(3)  # Operating Costs
            value.append(total_operating_expenses)
        
        if monthly_noi > 0:
            source.append(1)  # Effective Income
            target.append(4)  # NOI
            value.append(monthly_noi)
    
    # Stage 3: Operating Costs breakdown (bottom section)
    operating_expense_flows = [
        (3, 5, monthly_taxes, "Property Tax"),
        (3, 6, monthly_insurance, "Insurance"),
        (3, 7, monthly_repairs, "Repairs"),
        (3, 8, monthly_management, "Management"),
        (3, 9, monthly_other, "Other Costs")
    ]
    
    for src, tgt, val, name in operating_expense_flows:
        if val > 0:
            source.append(src)
            target.append(tgt)
            value.append(val)
    
    # Stage 4: NOI flows (top section)
    if monthly_noi > 0:
        if monthly_pi > 0:
            source.append(4)  # NOI
            target.append(10)  # Debt Service
            value.append(monthly_pi)
        
        if monthly_cash_flow != 0:
            source.append(4)  # NOI
            target.append(11)  # Net Cash Flow
            value.append(abs(monthly_cash_flow))
    
    # Enhanced color scheme
    node_colors = [
        "#2E8B57",    # Gross Rent - Forest Green
        "#4682B4",    # Effective Income - Steel Blue
        "#DC143C",    # Vacancy Loss - Crimson Red
        "#FF6347",    # Operating Costs - Tomato
        "#32CD32",    # NOI - Lime Green
        "#D2691E",    # Property Tax - Chocolate
        "#D2691E",    # Insurance - Chocolate
        "#D2691E",    # Repairs - Chocolate
        "#D2691E",    # Management - Chocolate
        "#D2691E",    # Other Costs - Chocolate
        "#8B0000",    # Debt Service - Dark Red
        "#228B22" if monthly_cash_flow >= 0 else "#DC143C"  # Net Cash Flow
    ]
    
    # Link colors
    link_colors = []
    for i, (src, tgt) in enumerate(zip(source, target)):
        if tgt == 2:  # Vacancy loss
            link_colors.append("rgba(220, 20, 60, 0.5)")  # Crimson
        elif tgt == 3:  # To operating costs
            link_colors.append("rgba(255, 99, 71, 0.5)")  # Tomato
        elif tgt == 4:  # To NOI
            link_colors.append("rgba(50, 205, 50, 0.5)")  # Lime Green
        elif src == 3:  # From operating costs to individual expenses
            link_colors.append("rgba(210, 105, 30, 0.5)")  # Chocolate
        elif tgt == 10:  # To debt service
            link_colors.append("rgba(139, 0, 0, 0.5)")  # Dark Red
        elif tgt == 11:  # To final cash flow
            if monthly_cash_flow >= 0:
                link_colors.append("rgba(34, 139, 34, 0.5)")  # Forest Green
            else:
                link_colors.append("rgba(220, 20, 60, 0.5)")  # Crimson
        else:
            link_colors.append("rgba(70, 130, 180, 0.5)")  # Steel Blue
    
    # Create Sankey diagram with optimized positioning
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,  # Reduced padding to fit better
            thickness=22,  # Slightly thinner nodes
            line=dict(color="black", width=0.8),
            label=labels,
            color=node_colors,
            # Adjusted positioning to fit within chart boundaries
            x=[0.05, 0.3, 0.1, 0.6, 0.6, 0.85, 0.85, 0.85, 0.85, 0.85, 0.75, 0.95],  # x positions - pulled in from edges
            y=[0.5, 0.5, 0.05, 0.25, 0.75, 0.08, 0.18, 0.28, 0.38, 0.48, 0.6, 0.85]   # y positions - adjusted for margins
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors
        )
    )])
    
    fig.update_layout(
        title_text="Monthly Cash Flow Analysis",
        font_size=12,  # Slightly smaller font to fit better
        height=700,  # Increased height for more space
        margin=dict(l=20, r=20, t=80, b=20),  # Increased margins all around
        plot_bgcolor='white',
        paper_bgcolor='white',
        # Ensure proper fit
        autosize=True
    )
    
    return fig

def main():
    # Header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🏢 Philadelphia Multifamily Property Analyzer")
    st.markdown("""
    *Analyze multifamily properties using PHA payment standards*
    
    **⚠️ NOT FINANCIAL ADVICE - [ACKNOWLEDGE DISCLAIMER](#important-legal-disclaimer-please-read) ⚠️**
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("🏠 Property Details")
        
        # ZIP Code selection
        zip_options = sorted(ZIP_TO_GROUP_MAPPING.keys())
        zip_code = st.selectbox(
            "ZIP Code",
            options=zip_options,
            index=zip_options.index("19121") if "19121" in zip_options else 0,
            help="Select the property's ZIP code to determine PHA group"
        )
        
        # Show neighborhood info
        if zip_code:
            neighborhood = get_client_friendly_neighborhood(zip_code)
            group = ZIP_TO_GROUP_MAPPING.get(zip_code)
            rent_type = GROUP_TO_RENT_TYPE.get(group)
            
            st.info(f"""
            **Neighborhood:** {neighborhood}
            
            **PHA Group:** {group} - {rent_type}
            """)
        
        # Unit configuration
        st.subheader("📋 Unit Configuration")
        unit_input = st.text_input(
            "Units",
            value="5x1BR, 3x2BR, 2x3BR",
            help="Enter units like '5x1BR, 3x2BR' or '1,2,3,1,1'"
        )
        
        # Financial details
        st.subheader("💰 Financial Details")
        property_price = st.number_input(
            "Property Price ($)",
            min_value=50000,
            value=500000,
            step=25000,
            format="%d"
        )
        
        down_payment = st.slider(
            "Down Payment (%)",
            min_value=0,
            max_value=100,
            value=25,
            step=5
        )
        
        col1, col2 = st.columns(2)
        with col1:
            interest_rate = st.number_input(
                "Interest Rate (%)",
                min_value=0.0,
                max_value=20.0,
                value=7.5,
                step=0.1
            )
        
        with col2:
            loan_term = st.selectbox(
                "Loan Term (years)",
                options=[15, 30],
                index=1
            )
        
        property_taxes = st.number_input(
            "Annual Property Taxes ($)",
            min_value=0,
            value=8000,
            step=500
        )
        
        insurance = st.number_input(
            "Annual Insurance ($)",
            min_value=0,
            value=3000,
            step=500
        )
        
        # Operating expenses
        st.subheader("🔧 Operating Expenses")
        vacancy_rate = st.slider(
            "Vacancy Rate (%)",
            min_value=0,
            max_value=30,
            value=5
        )
        
        repairs_rate = st.slider(
            "Repairs & Maintenance (% of rent)",
            min_value=0,
            max_value=20,
            value=5
        )
        
        management_rate = st.slider(
            "Property Management (% of rent)",
            min_value=0,
            max_value=15,
            value=8
        )
        
        other_expenses = st.number_input(
            "Other Annual Expenses ($)",
            min_value=0,
            value=2000,
            step=500
        )
        
        # Optional property info for PDF
        st.subheader("📄 Report Information (Optional)")
        property_address = st.text_input(
            "Property Address",
            placeholder="123 Main St, Philadelphia, PA"
        )
        
        property_notes = st.text_area(
            "Analysis Notes",
            placeholder="Add any notes about the property or analysis assumptions...",
            height=100
        )
        
        # Analyze button
        analyze_btn = st.button(
            "🔍 Analyze Property",
            type="primary",
            use_container_width=True
        )
    
    # Main content area
    if analyze_btn:
        with st.spinner("Analyzing property..."):
            # Prepare input parameters
            input_params = {
                "property_zip_code": zip_code,
                "unit_bedroom_counts_str": unit_input,
                "property_price": property_price,
                "down_payment_percent": down_payment,
                "annual_property_taxes": property_taxes,
                "annual_home_insurance": insurance,
                "vacancy_rate_percent": vacancy_rate,
                "repairs_maintenance_percent": repairs_rate,
                "property_management_percent": management_rate,
                "other_opex_annual": other_expenses
            }
            
            # Run analysis
            try:
                results = analyze_multifamily_property(
                    property_zip_code=zip_code,
                    unit_bedroom_counts_str=unit_input,
                    property_price=property_price,
                    annual_property_taxes=property_taxes,
                    annual_home_insurance=insurance,
                    loan_term_years=loan_term,
                    annual_interest_rate_percent=interest_rate,
                    down_payment_percent=down_payment,
                    vacancy_rate_percent=vacancy_rate,
                    repairs_maintenance_percent=repairs_rate,
                    property_management_percent=management_rate,
                    other_opex_annual=other_expenses
                )
                
                summary = results.get('property_summary', {})
                
                # Check for errors
                if summary.get('error'):
                    st.error(f"Analysis Error: {summary['error']}")
                    if summary.get('unit_errors'):
                        st.warning(f"Unit Parsing Details: {summary['unit_errors']}")
                    return
                
                # Display warnings if any
                if summary.get('unit_errors'):
                    st.warning(f"⚠️ Unit Parsing Notes: {summary['unit_errors']}")
                
                # Success - display results
                st.success("✅ Analysis completed successfully!")
                
                # Key metrics row
                st.subheader("📊 Key Investment Metrics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_rent = summary.get('total_potential_pha_rent_monthly', 0)
                    st.metric("Total Monthly Rent", f"${total_rent:,.0f}")
                
                with col2:
                    cap_rate = summary.get('cap_rate_percent', 0)
                    if cap_rate == float('inf'):
                        cap_rate_display = "∞"
                    else:
                        cap_rate_display = f"{cap_rate:.1f}%"
                    st.metric("Cap Rate", cap_rate_display)
                
                with col3:
                    coc = summary.get('cash_on_cash_return_percent', 0)
                    if coc == float('inf'):
                        coc_display = "∞"
                    elif coc == -float('inf'):
                        coc_display = "N/A"
                    else:
                        coc_display = f"{coc:.1f}%"
                    st.metric("Cash-on-Cash Return", coc_display)
                
                with col4:
                    monthly_cf = summary.get('cash_flow_before_tax_monthly', 0)
                    st.metric(
                        "Monthly Cash Flow",
                        f"${monthly_cf:,.0f}",
                        delta=None,
                        delta_color="normal" if monthly_cf >= 0 else "inverse"
                    )
                
                # Charts
                fig = create_charts(results)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                # Detailed results in tabs
                tab1, tab2, tab3 = st.tabs(["📋 Summary", "🏠 Unit Details", "📄 Full Report"])
                
                with tab1:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Property Overview")
                        st.write(f"**Purchase Price:** ${property_price:,}")
                        st.write(f"**Down Payment:** ${summary.get('down_payment_amount', 0):,.0f} ({down_payment}%)")
                        st.write(f"**Loan Amount:** ${property_price - summary.get('down_payment_amount', 0):,.0f}")
                        st.write(f"**Neighborhood:** {get_client_friendly_neighborhood(zip_code)}")
                    
                    with col2:
                        st.subheader("Annual Performance")
                        st.write(f"**Gross Potential Rent:** ${summary.get('total_potential_pha_rent_monthly', 0) * 12:,.0f}")
                        st.write(f"**Net Operating Income:** ${summary.get('noi_annual', 0):,.0f}")
                        st.write(f"**Annual Cash Flow:** ${summary.get('cash_flow_before_tax_annual', 0):,.0f}")
                        st.write(f"**GRM:** {summary.get('grm', 0):.1f}")
                
                with tab2:
                    st.subheader("Unit Breakdown")
                    units_data = []
                    for unit in results.get('units', []):
                        if 'error' not in unit:
                            units_data.append({
                                'Unit #': unit['unit_number'],
                                'Type': unit['bedrooms_str'],
                                'PHA Group': unit.get('safmr_group', 'N/A'),
                                'Rent Type': unit.get('rent_type', 'N/A'),
                                'Monthly Rent': f"${unit.get('pha_rent', 0):,.0f}"
                            })
                    
                    if units_data:
                        df = pd.DataFrame(units_data)
                        st.dataframe(df, use_container_width=True)
                
                with tab3:
                    st.subheader("Complete Analysis Report")
                    
                    # Generate full report
                    full_report = format_results_as_string(results, input_params)
                    st.text(full_report)
                    
                    # PDF download button
                    if PDF_AVAILABLE:
                        pdf_data, pdf_error = generate_pdf_report(
                            results, 
                            input_params, 
                            property_address or "Address not provided",
                            property_notes or "No additional notes"
                        )
                        
                        if pdf_data:
                            filename = f"multifamily_analysis_{zip_code}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                            st.download_button(
                                label="📥 Download PDF Report",
                                data=pdf_data,
                                file_name=filename,
                                mime="application/pdf"
                            )
                        else:
                            st.error(f"PDF generation failed: {pdf_error}")
                    else:
                        st.warning("PDF generation not available. Install reportlab to enable PDF downloads.")
                
            except Exception as e:
                st.error(f"Unexpected error during analysis: {str(e)}")
                st.exception(e)
    
    else:
        # Default state - show instructions
        st.markdown("""
        ## Welcome to the Philadelphia Multifamily Property Analyzer! 🏢
        
        This tool helps you analyze multifamily investment properties in Philadelphia using official PHA (Philadelphia Housing Authority) payment standards.
        
        ### How to Use:
        1. **Select ZIP Code** - Choose your property's location
        2. **Configure Units** - Enter unit mix (e.g., "5x1BR, 3x2BR")
        3. **Enter Financials** - Property price, down payment, rates
        4. **Set Operating Expenses** - Vacancy, maintenance, management rates
        5. **Click Analyze** - Get comprehensive investment analysis
        
        ### Features:
        - ✅ Official PHA payment standards by neighborhood
        - 📊 Key investment metrics (Cap Rate, Cash-on-Cash, Cash Flow)
        - 🏠 Unit-by-unit rent breakdown
        - 📄 Professional PDF reports
        - 📍 Philadelphia neighborhood mapping
        
        **Ready to analyze your next investment?** Fill out the form on the left and click "Analyze Property"!
        """)
        
        # Show sample PHA payment standards
        st.subheader("📋 Sample PHA Payment Standards by Group")
        
        sample_data = []
        for group, standards in PAYMENT_STANDARDS.items():
            rent_type = GROUP_TO_RENT_TYPE.get(group, "Unknown")
            sample_data.append({
                'PHA Group': group,
                'Rent Type': rent_type,
                '1 BR': f"${standards.get('1 BR', 0):,}",
                '2 BR': f"${standards.get('2 BR', 0):,}",
                '3 BR': f"${standards.get('3 BR', 0):,}"
            })
        
        df_sample = pd.DataFrame(sample_data)
        st.dataframe(df_sample, use_container_width=True)
    
    # Add disclaimer section at the bottom of every page
    st.markdown("---")
    
    # Disclaimer in an expandable section
    with st.expander("⚠️ Important Legal Disclaimer - Please Read", expanded=False):
        st.markdown("""
        <a name="important-legal-disclaimer-please-read"></a>
        
        ### EDUCATIONAL AND INFORMATIONAL PURPOSES ONLY
        
        This Philadelphia Multifamily Property Investment Calculator is provided for **educational and informational purposes only**. 
        
        **This calculator does NOT provide:**
        - Investment advice or recommendations
        - Financial planning or advisory services  
        - Tax or legal advice
        - Professional valuation services
        
        **Important Warnings:**
        - 📊 **No guarantee** of accuracy - calculations may contain errors
        - 📈 **Market conditions vary** - actual results may differ significantly
        - 🏠 **Property-specific factors** not considered in calculations
        - 💰 **Investment risk** - real estate investments can lose value
        
        **Before Making Investment Decisions:**
        - ✅ Consult licensed real estate professionals
        - ✅ Seek advice from CPAs and financial advisors
        - ✅ Conduct thorough due diligence
        - ✅ Verify all data independently
        - ✅ Consider all risks involved
        
        **User Responsibility:**
        By using this calculator, you acknowledge that you are solely responsible for your investment decisions 
        and will not rely solely on these calculations for making financial commitments.
        
        **Data Currency:** PHA payment standards based on data effective October 1, 2024. 
        Rates and regulations may change without notice.
        
        **Limitation of Liability:** To the maximum extent permitted by law, the creators of this calculator 
        shall not be liable for any damages, losses, or investment decisions made based on calculator results.
        
        **BY USING THIS CALCULATOR, YOU ACKNOWLEDGE THAT YOU HAVE READ AND AGREE TO THIS DISCLAIMER.**
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main())
    
    # Footer with additional legal info
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8em; padding: 20px;">
        <p>Philadelphia Multifamily Property Analyzer | For Educational Purposes Only<br>
        Always consult qualified professionals before making investment decisions<br>
        Last Updated: December 2024</p>
    </div>
    """, unsafe_allow_html=True
