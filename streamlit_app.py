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

# ============================================================================
# NEW: 2025 Payment Standards Data
# ============================================================================

# 2025 ZIP to Group Mapping (updated from November 2025 schedule)
ZIP_TO_GROUP_MAPPING_2025 = {
    # Group 1 - Basic Rents
    '19124': 'Group 1', '19132': 'Group 1', '19133': 'Group 1', '19141': 'Group 1',
    
    # Group 2 - Traditional Rents
    '19111': 'Group 2', '19115': 'Group 2', '19116': 'Group 2', '19119': 'Group 2',
    '19120': 'Group 2', '19121': 'Group 2', '19122': 'Group 2', '19126': 'Group 2',
    '19134': 'Group 2', '19135': 'Group 2', '19136': 'Group 2', '19137': 'Group 2',
    '19138': 'Group 2', '19139': 'Group 2', '19140': 'Group 2', '19142': 'Group 2',
    '19143': 'Group 2', '19144': 'Group 2', '19150': 'Group 2', '19151': 'Group 2',
    '19152': 'Group 2',
    
    # Group 3 - Mid Range Rents
    '19101': 'Group 3', '19104': 'Group 3', '19105': 'Group 3', '19109': 'Group 3',
    '19110': 'Group 3', '19112': 'Group 3', '19114': 'Group 3', '19129': 'Group 3',
    '19131': 'Group 3', '19145': 'Group 3', '19148': 'Group 3', '19149': 'Group 3',
    '19153': 'Group 3', '19154': 'Group 3',
    
    # Group 4 - Opportunity Rents
    '19118': 'Group 4', '19123': 'Group 4', '19125': 'Group 4', '19127': 'Group 4',
    '19128': 'Group 4', '19146': 'Group 4',
    
    # Group 5 - High Opportunity Rents
    '19102': 'Group 5', '19103': 'Group 5', '19106': 'Group 5', '19107': 'Group 5',
    '19130': 'Group 5', '19147': 'Group 5'
}

# 2025 Payment Standards
PAYMENT_STANDARDS_2025 = {
    'Group 1': {  # Basic Rents
        'SRO': 825, '0 BR': 1100, '1 BR': 1190, '2 BR': 1420, '3 BR': 1700,
        '4 BR': 1900, '5 BR': 2185, '6 BR': 2470, '7 BR': 2755, '8 BR': 3040
    },
    'Group 2': {  # Traditional Rents
        'SRO': 960, '0 BR': 1280, '1 BR': 1390, '2 BR': 1660, '3 BR': 1990,
        '4 BR': 2220, '5 BR': 2553, '6 BR': 2886, '7 BR': 3219, '8 BR': 3552
    },
    'Group 3': {  # Mid Range Rents
        'SRO': 1162, '0 BR': 1550, '1 BR': 1690, '2 BR': 2010, '3 BR': 2410,
        '4 BR': 2690, '5 BR': 3093, '6 BR': 3497, '7 BR': 3900, '8 BR': 4304
    },
    'Group 4': {  # Opportunity Rents
        'SRO': 1350, '0 BR': 1800, '1 BR': 1960, '2 BR': 2330, '3 BR': 2790,
        '4 BR': 3120, '5 BR': 3588, '6 BR': 4056, '7 BR': 4524, '8 BR': 4992
    },
    'Group 5': {  # High Opportunity Rents
        'SRO': 1575, '0 BR': 2100, '1 BR': 2280, '2 BR': 2720, '3 BR': 3260,
        '4 BR': 3640, '5 BR': 4186, '6 BR': 4732, '7 BR': 5278, '8 BR': 5824
    }
}

# 2025 Group to Rent Type Mapping
GROUP_TO_RENT_TYPE_2025 = {
    'Group 1': 'Basic Rents',
    'Group 2': 'Traditional Rents',
    'Group 3': 'Mid Range Rents',
    'Group 4': 'Opportunity Rents',
    'Group 5': 'High Opportunity Rents'
}

# ============================================================================
# Helper functions to get payment standard data based on year selection
# ============================================================================

def get_payment_standards_for_year(year):
    """Get payment standards for the specified year."""
    if year == "2025":
        return PAYMENT_STANDARDS_2025
    else:  # Default to 2024
        return PAYMENT_STANDARDS

def get_zip_mapping_for_year(year):
    """Get ZIP to group mapping for the specified year."""
    if year == "2025":
        return ZIP_TO_GROUP_MAPPING_2025
    else:  # Default to 2024
        return ZIP_TO_GROUP_MAPPING

def get_group_to_rent_type_for_year(year):
    """Get group to rent type mapping for the specified year."""
    if year == "2025":
        return GROUP_TO_RENT_TYPE_2025
    else:  # Default to 2024
        return GROUP_TO_RENT_TYPE

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
    .payment-standard-selector {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def generate_pdf_report(analysis_results, input_params, property_address="N/A", property_notes="N/A", payment_year="2024"):
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
        
        # Payment Standard Year
        payment_standard_text = f"<b>Payment Standards:</b> PHA {payment_year} Schedule"
        elements.append(Paragraph(payment_standard_text, normal_style))
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
    monthly_maintenance = summary.get('monthly_maintenance', 0)
    monthly_management = summary.get('monthly_management_fee', 0)
    monthly_opex = monthly_taxes + monthly_insurance + monthly_maintenance + monthly_management
    
    # NOI
    monthly_noi = effective_gross_income - monthly_opex
    
    # Debt service
    monthly_debt_service = summary.get('monthly_debt_service', 0)
    
    # Final cash flow
    monthly_cf = summary.get('cash_flow_before_tax_monthly', 0)
    
    # Build Sankey with NOI layer
    sankey_labels = [
        "Gross Rent",
        "Vacancy Loss",
        "Effective Income",
        "Property Taxes",
        "Insurance",
        "Maintenance",
        "Management",
        "NOI",
        "Debt Service",
        "Cash Flow"
    ]
    
    sankey_sources = []
    sankey_targets = []
    sankey_values = []
    sankey_colors = []
    
    # Gross Rent -> Vacancy and Effective Income
    if monthly_vacancy > 0:
        sankey_sources.append(0)  # Gross Rent
        sankey_targets.append(1)  # Vacancy Loss
        sankey_values.append(monthly_vacancy)
        sankey_colors.append('rgba(244, 67, 54, 0.4)')  # Red for loss
    
    sankey_sources.append(0)  # Gross Rent
    sankey_targets.append(2)  # Effective Income
    sankey_values.append(effective_gross_income)
    sankey_colors.append('rgba(76, 175, 80, 0.4)')  # Green for income flow
    
    # Effective Income -> Operating Expenses
    if monthly_taxes > 0:
        sankey_sources.append(2)
        sankey_targets.append(3)
        sankey_values.append(monthly_taxes)
        sankey_colors.append('rgba(255, 152, 0, 0.4)')
    
    if monthly_insurance > 0:
        sankey_sources.append(2)
        sankey_targets.append(4)
        sankey_values.append(monthly_insurance)
        sankey_colors.append('rgba(255, 152, 0, 0.4)')
    
    if monthly_maintenance > 0:
        sankey_sources.append(2)
        sankey_targets.append(5)
        sankey_values.append(monthly_maintenance)
        sankey_colors.append('rgba(255, 152, 0, 0.4)')
    
    if monthly_management > 0:
        sankey_sources.append(2)
        sankey_targets.append(6)
        sankey_values.append(monthly_management)
        sankey_colors.append('rgba(255, 152, 0, 0.4)')
    
    # Effective Income -> NOI
    sankey_sources.append(2)
    sankey_targets.append(7)  # NOI
    sankey_values.append(monthly_noi)
    sankey_colors.append('rgba(33, 150, 243, 0.4)')  # Blue for NOI
    
    # NOI -> Debt Service and Cash Flow
    if monthly_debt_service > 0:
        sankey_sources.append(7)  # NOI
        sankey_targets.append(8)  # Debt Service
        sankey_values.append(monthly_debt_service)
        sankey_colors.append('rgba(156, 39, 176, 0.4)')  # Purple for debt
    
    sankey_sources.append(7)  # NOI
    sankey_targets.append(9)  # Cash Flow
    sankey_values.append(max(monthly_cf, 0))
    if monthly_cf >= 0:
        sankey_colors.append('rgba(76, 175, 80, 0.6)')  # Green for positive CF
    else:
        sankey_colors.append('rgba(244, 67, 54, 0.6)')  # Red for negative CF
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="white", width=2),
            label=sankey_labels,
            color=['#4CAF50', '#F44336', '#2196F3', '#FF9800', '#FF9800', 
                   '#FF9800', '#FF9800', '#2196F3', '#9C27B0', 
                   '#4CAF50' if monthly_cf >= 0 else '#F44336']
        ),
        link=dict(
            source=sankey_sources,
            target=sankey_targets,
            value=sankey_values,
            color=sankey_colors
        )
    )])
    
    fig.update_layout(
        title="Monthly Cash Flow Analysis",
        font=dict(size=12),
        height=500
    )
    
    return fig

def main():
    # Header
    st.markdown('<div class="main-header"><h1>🏢 Philadelphia Multifamily Property Analyzer</h1></div>', 
                unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("Property Details")
        
        # ============================================================================
        # NEW: Payment Standard Year Selector
        # ============================================================================
        st.markdown('<div class="payment-standard-selector">', unsafe_allow_html=True)
        st.markdown("### 📅 Payment Standard Year")
        payment_year = st.radio(
            "Select PHA Payment Standard Schedule:",
            options=["2024", "2025"],
            index=0,  # Default to 2024
            help="Choose which PHA payment standard schedule to use for calculations. "
                 "2024 standards effective October 1, 2024. "
                 "2025 standards effective November 1, 2025."
        )
        
        # Show effective date based on selection
        if payment_year == "2025":
            st.info("📌 Using **November 2025** payment standards")
        else:
            st.info("📌 Using **October 2024** payment standards")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Get appropriate data structures based on year
        current_payment_standards = get_payment_standards_for_year(payment_year)
        current_zip_mapping = get_zip_mapping_for_year(payment_year)
        current_group_to_rent_type = get_group_to_rent_type_for_year(payment_year)
        
        # Property location
        st.subheader("📍 Location")
        
        # Get available ZIP codes from current mapping
        available_zips = sorted(current_zip_mapping.keys())
        
        zip_code = st.selectbox(
            "Property ZIP Code",
            options=available_zips,
            help="Select the ZIP code where the property is located"
        )
        
        # Show neighborhood and PHA group info
        if zip_code:
            neighborhood = get_client_friendly_neighborhood(zip_code)
            pha_group = current_zip_mapping.get(zip_code, 'Unknown')
            rent_type = current_group_to_rent_type.get(pha_group, 'Unknown')
            
            st.info(f"**Neighborhood:** {neighborhood}\n\n**PHA {payment_year} Group:** {pha_group} - {rent_type}")
        
        # Optional property details
        with st.expander("🏠 Additional Property Info (Optional)", expanded=False):
            property_address = st.text_input(
                "Property Address",
                help="Street address (optional, for report generation)"
            )
            
            property_notes = st.text_area(
                "Analysis Notes",
                help="Add any notes about this property (optional, included in PDF report)",
                placeholder="e.g., Property needs roof work, Great location near transit, etc."
            )
        
        st.markdown("---")
        
        # Unit configuration
        st.subheader("🏠 Unit Mix")
        unit_mix_str = st.text_input(
            "Unit Configuration",
            value="6x2BR, 4x1BR",
            help="Format: 'Number x Bedrooms'. Examples: '5x2BR, 3x1BR' or '10x1BR'"
        )
        
        st.markdown("---")
        
        # Financial inputs
        st.subheader("💰 Purchase & Financing")
        
        property_price = st.number_input(
            "Purchase Price ($)",
            min_value=0,
            value=500000,
            step=10000,
            help="Total purchase price of the property"
        )
        
        down_payment = st.slider(
            "Down Payment (%)",
            min_value=0,
            max_value=100,
            value=25,
            step=5,
            help="Percentage of purchase price paid as down payment"
        )
        
        interest_rate = st.number_input(
            "Interest Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=7.0,
            step=0.125,
            help="Annual interest rate for the mortgage"
        )
        
        loan_term_years = st.selectbox(
            "Loan Term (years)",
            options=[15, 20, 25, 30],
            index=3,
            help="Length of the mortgage in years"
        )
        
        st.markdown("---")
        
        # Operating expenses
        st.subheader("📊 Operating Expenses")
        
        annual_property_tax = st.number_input(
            "Annual Property Tax ($)",
            min_value=0,
            value=5000,
            step=100,
            help="Total annual property tax"
        )
        
        annual_insurance = st.number_input(
            "Annual Insurance ($)",
            min_value=0,
            value=2000,
            step=100,
            help="Annual property insurance premium"
        )
        
        vacancy_rate = st.slider(
            "Vacancy Rate (%)",
            min_value=0,
            max_value=30,
            value=5,
            step=1,
            help="Expected percentage of time units are vacant"
        )
        
        maintenance_rate = st.slider(
            "Maintenance Rate (%)",
            min_value=0,
            max_value=30,
            value=10,
            step=1,
            help="Percentage of gross rent for maintenance and repairs"
        )
        
        management_fee_rate = st.slider(
            "Management Fee (%)",
            min_value=0,
            max_value=20,
            value=8,
            step=1,
            help="Property management fee as percentage of gross rent"
        )
        
        st.markdown("---")
        
        # Analyze button
        analyze_button = st.button("🔍 Analyze Property", type="primary", use_container_width=True)
    
    # Main content area
    if analyze_button:
        # Validate inputs
        if not zip_code:
            st.error("Please select a ZIP code")
            return
        
        if not unit_mix_str.strip():
            st.error("Please enter unit configuration")
            return
        
        # Show loading spinner
        with st.spinner('Analyzing property...'):
            try:
                # Prepare input parameters
                input_params = {
                    'property_zip_code': zip_code,
                    'unit_mix_str': unit_mix_str,
                    'property_price': property_price,
                    'down_payment_percent': down_payment,
                    'interest_rate': interest_rate,
                    'loan_term_years': loan_term_years,
                    'annual_property_tax': annual_property_tax,
                    'annual_insurance': annual_insurance,
                    'vacancy_rate': vacancy_rate,
                    'maintenance_rate': maintenance_rate,
                    'management_fee_rate': management_fee_rate,
                    'payment_year': payment_year  # NEW: Pass payment year to calculator
                }
                
                # Run analysis
                # NOTE: The analyze_multifamily_property function needs to be updated
                # to accept and use the payment_year parameter
                results = analyze_multifamily_property(input_params)
                
                # Check for errors
                if 'property_summary' in results and results['property_summary'].get('error'):
                    st.error(f"Analysis Error: {results['property_summary']['error']}")
                    return
                
                # Display results
                st.success("✅ Analysis Complete!")
                
                summary = results['property_summary']
                
                # Key metrics in columns
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    cap_rate = summary.get('cap_rate_percent', 0)
                    st.metric("Cap Rate", f"{cap_rate:.2f}%")
                
                with col2:
                    noi = summary.get('noi_annual', 0)
                    st.metric("Annual NOI", f"${noi:,.0f}")
                
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
                        st.write(f"**Payment Standards:** PHA {payment_year}")
                    
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
                            property_notes or "No additional notes",
                            payment_year  # NEW: Pass payment year to PDF generator
                        )
                        
                        if pdf_data:
                            filename = f"multifamily_analysis_{zip_code}_{payment_year}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
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
        1. **Select Payment Standard Year** - Choose 2024 or 2025 PHA standards
        2. **Select ZIP Code** - Choose your property's location
        3. **Configure Units** - Enter unit mix (e.g., "5x1BR, 3x2BR")
        4. **Enter Financials** - Property price, down payment, rates
        5. **Set Operating Expenses** - Vacancy, maintenance, management rates
        6. **Click Analyze** - Get comprehensive investment analysis
        
        ### Features:
        - ✅ Official PHA payment standards by neighborhood (2024 & 2025)
        - 📊 Key investment metrics (Cap Rate, Cash-on-Cash, Cash Flow)
        - 🏠 Unit-by-unit rent breakdown
        - 📄 Professional PDF reports
        - 📍 Philadelphia neighborhood mapping
        
        **Ready to analyze your next investment?** Fill out the form on the left and click "Analyze Property"!
        """)
        
        # Show sample PHA payment standards for selected year
        st.subheader(f"📋 Sample PHA Payment Standards by Group ({payment_year if 'payment_year' in locals() else '2024'})")
        
        # Get current payment standards
        display_standards = get_payment_standards_for_year(st.session_state.get('payment_year', '2024'))
        display_rent_types = get_group_to_rent_type_for_year(st.session_state.get('payment_year', '2024'))
        
        sample_data = []
        for group, standards in display_standards.items():
            rent_type = display_rent_types.get(group, "Unknown")
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
        
        **Data Currency:** PHA payment standards based on official schedules: 
        - 2024: Effective October 1, 2024
        - 2025: Effective November 1, 2025
        
        Rates and regulations may change without notice.
        
        **Limitation of Liability:** To the maximum extent permitted by law, the creators of this calculator 
        shall not be liable for any damages, losses, or investment decisions made based on calculator results.
        
        **BY USING THIS CALCULATOR, YOU ACKNOWLEDGE THAT YOU HAVE READ AND AGREE TO THIS DISCLAIMER.**
        """, unsafe_allow_html=True)
    
    # Footer with additional legal info
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8em; padding: 20px;">
        <p>Philadelphia Multifamily Property Analyzer | For Educational Purposes Only<br>
        Always consult qualified professionals before making investment decisions<br>
        Last Updated: January 2025 | Now supporting 2024 & 2025 PHA Payment Standards</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
