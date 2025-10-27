# calculator.py - Philadelphia Multifamily Property Analysis Core Functions
"""
Philadelphia Multifamily Property Investment Calculator
Supports both 2024 and 2025 PHA Payment Standards
- 2024 Data: Effective October 1, 2024
- 2025 Data: Effective November 1, 2025
"""

import re
from io import StringIO

# ============================================================================
# 2024 PAYMENT STANDARDS (Original Data)
# ============================================================================

# Data effective October 1, 2024, from the provided document
ZIP_TO_GROUP_MAPPING = {
     # -------- Group 1 | Traditional Rents (blue) --------
    "19120": 1, "19124": 1, "19126": 1, "19132": 1, "19133": 1,
    "19134": 1, "19136": 1, "19139": 1, "19140": 1, "19141": 1,
    "19142": 1, "19143": 1, "19151": 1,

    # -------- Group 2 | Mid-Range Rents (light-blue) --------
    "19101": 2, "19104": 2, "19105": 2, "19109": 2, "19110": 2,
    "19111": 2, "19112": 2, "19114": 2, "19115": 2, "19116": 2,
    "19119": 2, "19121": 2, "19122": 2, "19131": 2, "19135": 2,
    "19137": 2, "19138": 2, "19144": 2, "19145": 2, "19148": 2,
    "19149": 2, "19150": 2, "19152": 2, "19153": 2, "19154": 2,

    # -------- Group 3 | Opportunity Rents (green) --------
    "19118": 3, "19125": 3, "19127": 3, "19128": 3,
    "19129": 3, "19146": 3,

    # -------- Group 4 | High-Opportunity Rents (yellow) --------
    "19102": 4, "19103": 4, "19106": 4, "19107": 4,
    "19123": 4, "19130": 4, "19147": 4,
}

PAYMENT_STANDARDS = {
    1: {  # Group 1 - Traditional Rents
        'SRO': 847, '0 BR': 1130, '1 BR': 1240, '2 BR': 1480, '3 BR': 1780,
        '4 BR': 2030, '5 BR': 2334, '6 BR': 2639, '7 BR': 2943, '8 BR': 3248
    },
    2: {  # Group 2 - Mid Range Rents
        'SRO': 1042, '0 BR': 1390, '1 BR': 1540, '2 BR': 1830, '3 BR': 2200,
        '4 BR': 2510, '5 BR': 2886, '6 BR': 3263, '7 BR': 3639, '8 BR': 4016
    },
    3: {  # Group 3 - Opportunity Rents
        'SRO': 1342, '0 BR': 1790, '1 BR': 1970, '2 BR': 2350, '3 BR': 2830,
        '4 BR': 3220, '5 BR': 3703, '6 BR': 4186, '7 BR': 4669, '8 BR': 5152
    },
    4: {  # Group 4 - High Opportunity Rents
        'SRO': 1522, '0 BR': 2030, '1 BR': 2270, '2 BR': 2700, '3 BR': 3250,
        '4 BR': 3700, '5 BR': 4255, '6 BR': 4810, '7 BR': 5365, '8 BR': 5920
    }
}

GROUP_TO_RENT_TYPE = {
    1: "Traditional Rents",
    2: "Mid Range Rents",
    3: "Opportunity Rents",
    4: "High Opportunity Rents"
}

# ============================================================================
# 2025 PAYMENT STANDARDS (New Data)
# ============================================================================

# Data effective November 1, 2025
ZIP_TO_GROUP_MAPPING_2025 = {
    # -------- Group 1 | Basic Rents --------
    "19124": 1, "19132": 1, "19133": 1, "19141": 1,
    
    # -------- Group 2 | Traditional Rents --------
    "19111": 2, "19115": 2, "19116": 2, "19119": 2,
    "19120": 2, "19121": 2, "19122": 2, "19126": 2,
    "19134": 2, "19135": 2, "19136": 2, "19137": 2,
    "19138": 2, "19139": 2, "19140": 2, "19142": 2,
    "19143": 2, "19144": 2, "19150": 2, "19151": 2,
    "19152": 2,
    
    # -------- Group 3 | Mid Range Rents --------
    "19101": 3, "19104": 3, "19105": 3, "19109": 3,
    "19110": 3, "19112": 3, "19114": 3, "19129": 3,
    "19131": 3, "19145": 3, "19148": 3, "19149": 3,
    "19153": 3, "19154": 3,
    
    # -------- Group 4 | Opportunity Rents --------
    "19118": 4, "19123": 4, "19125": 4, "19127": 4,
    "19128": 4, "19146": 4,
    
    # -------- Group 5 | High Opportunity Rents --------
    "19102": 5, "19103": 5, "19106": 5, "19107": 5,
    "19130": 5, "19147": 5
}

PAYMENT_STANDARDS_2025 = {
    1: {  # Group 1 - Basic Rents
        'SRO': 825, '0 BR': 1100, '1 BR': 1190, '2 BR': 1420, '3 BR': 1700,
        '4 BR': 1900, '5 BR': 2185, '6 BR': 2470, '7 BR': 2755, '8 BR': 3040
    },
    2: {  # Group 2 - Traditional Rents
        'SRO': 960, '0 BR': 1280, '1 BR': 1390, '2 BR': 1660, '3 BR': 1990,
        '4 BR': 2220, '5 BR': 2553, '6 BR': 2886, '7 BR': 3219, '8 BR': 3552
    },
    3: {  # Group 3 - Mid Range Rents
        'SRO': 1162, '0 BR': 1550, '1 BR': 1690, '2 BR': 2010, '3 BR': 2410,
        '4 BR': 2690, '5 BR': 3093, '6 BR': 3497, '7 BR': 3900, '8 BR': 4304
    },
    4: {  # Group 4 - Opportunity Rents
        'SRO': 1350, '0 BR': 1800, '1 BR': 1960, '2 BR': 2330, '3 BR': 2790,
        '4 BR': 3120, '5 BR': 3588, '6 BR': 4056, '7 BR': 4524, '8 BR': 4992
    },
    5: {  # Group 5 - High Opportunity Rents
        'SRO': 1575, '0 BR': 2100, '1 BR': 2280, '2 BR': 2720, '3 BR': 3260,
        '4 BR': 3640, '5 BR': 4186, '6 BR': 4732, '7 BR': 5278, '8 BR': 5824
    }
}

GROUP_TO_RENT_TYPE_2025 = {
    1: "Basic Rents",
    2: "Traditional Rents",
    3: "Mid Range Rents",
    4: "Opportunity Rents",
    5: "High Opportunity Rents"
}

# ============================================================================
# NEIGHBORHOOD GROUPINGS (Same for both years)
# ============================================================================

NEIGHBORHOOD_ZIP_GROUPINGS = {
    # --- Center City & Adjacent ---
    "Center City Core": ["19102", "19103", "19107"], # Rittenhouse, Logan Sq, Wash Sq West, Midtown Village, Avenue of the Arts
    "Old City / Society Hill / Waterfront": ["19106"],
    "Northern Liberties / Fishtown (South)": ["19123"], # Often seen as distinct but geographically close
    "Fairmount / Art Museum Area": ["19130"],
    "Graduate Hospital / Fitler Square": ["19146"], # Sometimes "Southwest Center City"
    "Bella Vista / Queen Village / Pennsport (South Philly East)": ["19147"],

    # --- South Philadelphia ---
    "South Philly - East (Passyunk, Dickinson Narrows)": ["19148"], # Distinct from 19147's more northern parts
    "South Philly - West (Point Breeze, Newbold, Girard Estate)": ["19145"],
    "South Philly - Deep South / Stadium District": ["19112"], # Navy Yard, Sports Complex area

    # --- West Philadelphia ---
    "University City / Spruce Hill / Walnut Hill": ["19104"], # UCity core, adjacent residential
    "West Philly - Central (Cedar Park, Garden Court, Cobbs Creek)": ["19143"],
    "West Philly - North (Mantua, Powelton Village, West Powelton)": ["19101", "19139"], # 19101 also covers 30th St Station area
    "Overbrook / Wynnefield": ["19131"],
    "Parkside / Carroll Park": ["19151"], # Western edge of West Philly

    # --- North Philadelphia ---
    "Fishtown (North) / Kensington (South) / Port Richmond (South)": ["19125"], # Fishtown core, parts of Kensington
    "Temple University Area / Lower North Philly": ["19121", "19122"], # Broad St corridor, Cecil B Moore
    "Brewerytown / Sharswood / Strawberry Mansion (East Fairmount Park)": ["19132"],
    "North Philly - East (Kensington, Harrowgate, Fairhill)": ["19133", "19134"], # More specific than just "Kensington"
    "Port Richmond / Bridesburg / Frankford (South)": ["19137"], # River Wards

    # --- Northwest Philadelphia ---
    "Germantown": ["19138", "19144"], # Can be split (East/West Germantown) but often grouped
    "Mount Airy": ["19119"],
    "Chestnut Hill": ["19118"],
    "Roxborough / Manayunk / East Falls": ["19127", "19128", "19129"], # Often grouped as "River Wards NW" or by individual names

    # --- Northeast Philadelphia ---
    "Lower Northeast (Frankford, Mayfair, Tacony)": ["19124", "19135", "19136"],
    "Central Northeast (Rhawnhurst, Fox Chase, Bustleton)": ["19111", "19115", "19152"],
    "Far Northeast (Somerton, Torresdale, Parkwood)": ["19114", "19116", "19154"],
    "Olney / Logan / Feltonville": ["19120", "19141"], # Upper North/Lower Northeast boundary
    "Oxford Circle / Lawncrest": ["19149"],
    "East Oak Lane / West Oak Lane": ["19126"],
    "Pennypack / Holmesburg": ["19150"], # Note: 19150 is Mt. Airy/W. Oak Lane more than Pennypack. Re-evaluating 19150.
                                         # 19150 is more aligned with Mt. Airy / Cedarbrook / West Oak Lane.
                                         # Let's re-assign 19150.
    # Re-evaluation for 19150:
    # "Mount Airy / Cedarbrook / West Oak Lane": ["19150", "19119", "19126"] - This makes more sense.
    # Let's adjust the NW Philly and Olney/Logan groups to reflect this.

    # --- Data Integrity Checks & Unassigned (From Original PHA List) ---
    # These are ZIPs from your PHA SAFMR mapping. Let's ensure they are covered.
    # 19105: Independence Hall area - could be "Old City / Society Hill" or "Center City Core"
    # 19109: Broad & Vine area - "Center City Core" or "Chinatown/Convention Center"
    # 19110: USPS ZIP, often not residential.
    # 19140: Hunting Park / Nicetown-Tioga - "North Philly - Central"
    # 19142: Southwest Philly (Elmwood, Eastwick)
    # 19153: Southwest Philly (Airport, Eastwick)

    # ----- REVISED GROUPINGS based on above logic & checks -----
    "Center City Core / Convention Center": ["19102", "19103", "19107", "19109"],
    "Old City / Society Hill / Independence Hall": ["19106", "19105"],
    "Northern Liberties / Fishtown (South)": ["19123"],
    "Fairmount / Art Museum Area": ["19130"],
    "Graduate Hospital / Fitler Square": ["19146"],
    "Bella Vista / Queen Village / Pennsport": ["19147"],

    "South Philly - East (Passyunk, Dickinson Narrows)": ["19148"],
    "South Philly - West (Point Breeze, Newbold, Girard Estate)": ["19145"],
    "South Philly - Deep South / Stadium District / Navy Yard": ["19112"],

    "University City / Spruce Hill / Walnut Hill": ["19104"],
    "West Philly - Central (Cedar Park, Garden Court, Cobbs Creek)": ["19143"],
    "West Philly - North (Mantua, Powelton, Mill Creek)": ["19139"], # 19101 is 30th St, less residential focus here
    "Overbrook / Wynnefield": ["19131"],
    "Parkside / Carroll Park / Haddington": ["19151"],

    "Fishtown (North) / Kensington (South) / Port Richmond (South)": ["19125"],
    "Temple University Area / Lower North Philly (Yorktown, Ludlow)": ["19121", "19122"],
    "Brewerytown / Sharswood / Strawberry Mansion": ["19132"],
    "North Philly - East (Kensington, Harrowgate, Fairhill, Juniata)": ["19133", "19134"],
    "Port Richmond / Bridesburg": ["19137"], # Keeping Frankford separate for now
    "North Philly - Central (Nicetown-Tioga, Hunting Park)": ["19140"],

    "Germantown (East & West)": ["19138", "19144"],
    "Mount Airy / Cedarbrook": ["19119", "19150"], # Grouped more closely
    "West Oak Lane / East Oak Lane": ["19126"], # Grouped
    "Chestnut Hill": ["19118"],
    "Roxborough / Manayunk / East Falls": ["19127", "19128", "19129"],

    "Lower Northeast (Frankford, Mayfair, Tacony, Wissinoming)": ["19124", "19135", "19136"],
    "Central Northeast (Rhawnhurst, Fox Chase, Bustleton, Somerton West)": ["19111", "19115", "19152"],
    "Far Northeast (Somerton East, Torresdale, Parkwood, Byberry)": ["19114", "19116", "19154"],
    "Olney / Logan / Feltonville": ["19120", "19141"],
    "Oxford Circle / Lawncrest / Lawndale": ["19149"],

    "Southwest Philly (Eastwick, Elmwood, Clearview)": ["19142", "19153"],

    # Special/Less Residential ZIPs (might not be in your PHA list for housing but good to know)
    "Center City - 30th Street Station Area": ["19101"], # Primarily commercial/transport
    "Special/Industrial/Non-Residential": ["19110"], # e.g., USPS & commercial
}

def get_client_friendly_neighborhood(zip_code_str):
    """
    Map a ZIP code to a client-friendly neighborhood name.
    """
    for neighborhood_name, zip_list in NEIGHBORHOOD_ZIP_GROUPINGS.items():
        if zip_code_str in zip_list:
            return neighborhood_name
    return f"ZIP {zip_code_str} Area (No specific neighborhood mapping available)"

# ============================================================================
# HELPER FUNCTIONS FOR YEAR SELECTION
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

# ============================================================================
# CORE CALCULATION FUNCTIONS
# ============================================================================

def parse_unit_bedroom_counts(unit_str):
    """
    Parse unit bedroom counts from a string like "6x2BR, 4x1BR" or "5 x 1 BR, 3 x 2 BR".
    """
    if not unit_str or not isinstance(unit_str, str):
        return [], "Invalid or empty unit string."

    unit_str_clean = unit_str.strip().upper()
    unit_patterns = re.split(r'[,;\s]+AND\s+|[,;]', unit_str_clean)

    parsed_units = []
    errors = []

    for pattern in unit_patterns:
        pattern = pattern.strip()
        if not pattern:
            continue

        match = re.match(r'(\d+)\s*[xX×]\s*(\d+)\s*BR', pattern)
        if match:
            count = int(match.group(1))
            br_num = int(match.group(2))
            parsed_units.append({'count': count, 'bedrooms': br_num})
        else:
            errors.append(f"Could not parse '{pattern}'")

    if errors:
        return parsed_units, "; ".join(errors)
    return parsed_units, None

def calculate_loan_payment(principal, annual_rate, term_years):
    """
    Calculate monthly mortgage payment using standard amortization formula.
    """
    if principal <= 0 or term_years <= 0:
        return 0.0
    if annual_rate == 0:
        return principal / (term_years * 12)

    monthly_rate = annual_rate / 100.0 / 12.0
    num_payments = term_years * 12
    monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                      ((1 + monthly_rate) ** num_payments - 1)
    return monthly_payment

def analyze_multifamily_property(input_params):
    """
    Main analysis function that supports both 2024 and 2025 payment standards.
    
    Args:
        input_params: Dictionary containing:
            - property_zip_code
            - unit_bedroom_counts_str  
            - property_price
            - down_payment_percent
            - interest_rate
            - loan_term_years
            - annual_property_taxes
            - annual_home_insurance
            - vacancy_rate_percent
            - repairs_maintenance_percent
            - property_management_percent
            - other_opex_annual
            - payment_year (optional, defaults to "2024")
    
    Returns:
        Dictionary with 'units' and 'property_summary' keys
    """
    
    # Extract payment year (default to 2024 if not provided)
    payment_year = input_params.get('payment_year', '2024')
    
    # Get appropriate data structures based on year
    zip_mapping = get_zip_mapping_for_year(payment_year)
    payment_standards = get_payment_standards_for_year(payment_year)
    group_to_rent_type = get_group_to_rent_type_for_year(payment_year)
    
    # Extract input parameters
    prop_zip = input_params['property_zip_code']
    unit_mix_str = input_params['unit_bedroom_counts_str']
    prop_price = float(input_params['property_price'])
    dp_percent = float(input_params['down_payment_percent'])
    interest_rate_annual = float(input_params['interest_rate'])
    loan_term_years = int(input_params['loan_term_years'])
    annual_property_tax = float(input_params['annual_property_taxes'])
    annual_insurance = float(input_params['annual_home_insurance'])
    vacancy_rate = float(input_params['vacancy_rate_percent'])
    maintenance_rate = float(input_params['repairs_maintenance_percent'])
    management_rate = float(input_params['property_management_percent'])
    other_opex = float(input_params['other_opex_annual'])

    # Initialize result structure
    result = {
        'units': [],
        'property_summary': {}
    }

    # Parse unit mix
    parsed_units, parse_error = parse_unit_bedroom_counts(unit_mix_str)
    
    if parse_error:
        result['property_summary']['unit_errors'] = parse_error

    if not parsed_units:
        result['property_summary']['error'] = "No valid units found to analyze."
        return result

    # Get SAFMR group for this ZIP
    safmr_group = zip_mapping.get(prop_zip)
    
    if safmr_group is None:
        result['property_summary']['error'] = f"ZIP code {prop_zip} not found in {payment_year} payment standards."
        return result

    rent_type = group_to_rent_type.get(safmr_group, "Unknown")
    group_payment_standards = payment_standards.get(safmr_group, {})

    # Process each unit
    unit_number = 0
    total_monthly_rent = 0.0

    for unit_group in parsed_units:
        count = unit_group['count']
        bedrooms = unit_group['bedrooms']
        bedrooms_str = f"{bedrooms} BR"

        # Get PHA rent for this bedroom type
        pha_rent = group_payment_standards.get(bedrooms_str, None)

        for _ in range(count):
            unit_number += 1
            unit_info = {
                'unit_number': unit_number,
                'bedrooms': bedrooms,
                'bedrooms_str': bedrooms_str,
                'safmr_group': safmr_group,
                'rent_type': rent_type
            }

            if pha_rent is not None:
                unit_info['pha_rent'] = float(pha_rent)
                total_monthly_rent += pha_rent
            else:
                unit_info['error'] = f"No PHA rent standard found for {bedrooms_str} in Group {safmr_group}"
                unit_info['pha_rent'] = 0.0

            result['units'].append(unit_info)

    # Calculate property financials
    down_payment_amount = prop_price * (dp_percent / 100.0)
    loan_amount = prop_price - down_payment_amount

    # Calculate monthly P&I
    monthly_pi = calculate_loan_payment(loan_amount, interest_rate_annual, loan_term_years)
    monthly_taxes = annual_property_tax / 12.0
    monthly_insurance = annual_insurance / 12.0
    monthly_piti = monthly_pi + monthly_taxes + monthly_insurance

    # Annual calculations
    gross_potential_rent_annual = total_monthly_rent * 12
    vacancy_allowance_annual = gross_potential_rent_annual * (vacancy_rate / 100.0)
    effective_gross_income_annual = gross_potential_rent_annual - vacancy_allowance_annual

    repairs_allowance_annual = gross_potential_rent_annual * (maintenance_rate / 100.0)
    management_fee_annual = gross_potential_rent_annual * (management_rate / 100.0)

    total_operating_expenses_annual = (
        annual_property_tax +
        annual_insurance +
        repairs_allowance_annual +
        management_fee_annual +
        other_opex
    )

    noi_annual = effective_gross_income_annual - total_operating_expenses_annual
    annual_debt_service = monthly_pi * 12

    cash_flow_before_tax_annual = noi_annual - annual_debt_service
    cash_flow_before_tax_monthly = cash_flow_before_tax_annual / 12.0

    # Calculate returns
    total_cash_invested = down_payment_amount

    if total_cash_invested > 0:
        cash_on_cash_return = (cash_flow_before_tax_annual / total_cash_invested) * 100.0
    elif cash_flow_before_tax_annual > 0:
        cash_on_cash_return = float('inf')
    else:
        cash_on_cash_return = -float('inf')

    if prop_price > 0:
        cap_rate = (noi_annual / prop_price) * 100.0
    else:
        cap_rate = float('inf')

    if gross_potential_rent_annual > 0:
        grm = prop_price / gross_potential_rent_annual
    else:
        grm = 0.0

    # 5-year projections
    gross_revenue_5_years = gross_potential_rent_annual * 5
    noi_5_years = noi_annual * 5

    # Build summary
    result['property_summary'] = {
        'total_units': unit_number,
        'safmr_group': safmr_group,
        'rent_type': rent_type,
        'payment_year': payment_year,  # NEW: Include payment year in results
        'total_potential_pha_rent_monthly': total_monthly_rent,
        'down_payment_amount': down_payment_amount,
        'loan_amount': loan_amount,
        'monthly_principal_interest': monthly_pi,
        'monthly_taxes': monthly_taxes,
        'monthly_insurance': monthly_insurance,
        'monthly_piti': monthly_piti,
        'monthly_maintenance': repairs_allowance_annual / 12.0,
        'monthly_management_fee': management_fee_annual / 12.0,
        'monthly_debt_service': monthly_pi,
        'gross_potential_rent_annual': gross_potential_rent_annual,
        'vacancy_allowance_annual': vacancy_allowance_annual,
        'effective_gross_income_annual': effective_gross_income_annual,
        'repairs_allowance_annual': repairs_allowance_annual,
        'management_fee_annual': management_fee_annual,
        'total_operating_expenses_annual': total_operating_expenses_annual,
        'noi_annual': noi_annual,
        'annual_debt_service': annual_debt_service,
        'cash_flow_before_tax_annual': cash_flow_before_tax_annual,
        'cash_flow_before_tax_monthly': cash_flow_before_tax_monthly,
        'cash_on_cash_return_percent': cash_on_cash_return,
        'cap_rate_percent': cap_rate,
        'grm': grm,
        'gross_revenue_5_years': gross_revenue_5_years,
        'noi_5_years': noi_5_years,
    }

    return result

def format_results_as_string(analysis_results, input_params):
    """
    Format analysis results as a string for display or export.
    """
    output_buffer = StringIO()
    
    units_info = analysis_results.get('units', [])
    summary = analysis_results.get('property_summary', {})

    # Extract input parameters
    prop_zip = input_params['property_zip_code']
    prop_price = input_params['property_price']
    dp_percent = input_params['down_payment_percent']
    annual_taxes = input_params['annual_property_taxes']
    annual_insurance = input_params['annual_home_insurance']
    vac_rate = input_params['vacancy_rate_percent']
    rep_maint_percent = input_params['repairs_maintenance_percent']
    prop_mgmt_percent = input_params['property_management_percent']
    other_opex = input_params['other_opex_annual']
    payment_year = input_params.get('payment_year', '2024')  # NEW: Get payment year

    # Get client-friendly neighborhood
    try:
        client_neighborhood = get_client_friendly_neighborhood(prop_zip)
    except:
        client_neighborhood = "N/A (Lookup function not found)"

    output_buffer.write("--- MULTIFAMILY CALCULATION RESULTS ---\n")
    output_buffer.write(f"PHA Payment Standards: {payment_year}\n")  # NEW: Display payment year
    output_buffer.write(f"Input Unit String: {input_params['unit_bedroom_counts_str']}\n")
    output_buffer.write(f"Property ZIP Code: {prop_zip}\n")
    output_buffer.write(f"Client-Friendly Area: {client_neighborhood}\n")

    if summary.get('error') and not summary.get('unit_errors'):
        output_buffer.write(f"🚨 Error during calculation: {summary['error']}\n")
        if 'unit_errors' in summary:
             output_buffer.write(f"Individual Unit Errors: {summary['unit_errors']}\n")
    elif summary.get('error') and summary.get('unit_errors') and "No valid units found" in summary.get('error',''):
        output_buffer.write(f"🚨 Error: {summary['error']}\n")
        output_buffer.write(f"Details on Unit Parsing: {summary['unit_errors']}\n")
    else:
        try:
            if summary.get('unit_errors'):
                 output_buffer.write(f"⚠️ Note on Units/Parsing: {summary['unit_errors']}\n")
            output_buffer.write("-" * 50 + "\n")

            output_buffer.write(f"Unit Breakdown (Potential PHA Rents) - Total {len(units_info)} units processed:\n")
            valid_units_for_rent_calc = 0
            for unit in units_info:
                if 'error' in unit:
                    output_buffer.write(f"  Unit {unit['unit_number']} (Input: '{unit['bedrooms_str']}'): Error - {unit['error']}\n")
                else:
                    output_buffer.write(f"  Unit {unit['unit_number']} (Input: '{unit['bedrooms_str']}', Type: {unit.get('rent_type', 'N/A')}): ${unit.get('pha_rent', 0.0):.2f}/mo (Group {unit.get('safmr_group','N/A')})\n")
                    valid_units_for_rent_calc +=1

            if valid_units_for_rent_calc < len(units_info):
                output_buffer.write(f"  ({valid_units_for_rent_calc} of {len(units_info)} units were valid for rent calculation)\n")

            total_monthly_pha_rent = summary.get('total_potential_pha_rent_monthly', 0.0)
            output_buffer.write(f"  Total Potential Monthly PHA Rent (All Valid Units): ${total_monthly_pha_rent:,.2f}\n")
            output_buffer.write("-" * 50 + "\n")

            output_buffer.write("Property Financial Summary:\n")
            output_buffer.write(f"  Acquisition Price: ${float(prop_price):,.2f}\n")
            output_buffer.write(f"  Down Payment ({dp_percent}%): ${summary.get('down_payment_amount', 0.0):,.2f}\n")
            output_buffer.write("-" * 50 + "\n")

            output_buffer.write("Monthly Debt Service (PITI) & Basic Cash Flow:\n")
            monthly_piti = summary.get('monthly_piti', 0.0)
            output_buffer.write(f"  Total Monthly PITI: ${monthly_piti:,.2f}\n")
            output_buffer.write(f"    Principal & Interest (P&I): ${summary.get('monthly_principal_interest', 0.0):,.2f}\n")
            output_buffer.write(f"    Property Taxes (T): ${summary.get('monthly_taxes', 0.0):,.2f}\n")
            output_buffer.write(f"    Property Insurance (I): ${summary.get('monthly_insurance', 0.0):,.2f}\n")

            simple_cash_flow_monthly = total_monthly_pha_rent - monthly_piti
            if simple_cash_flow_monthly >= 0:
                output_buffer.write(f"  Basic Monthly Cash Flow (Total Rent - PITI): ${simple_cash_flow_monthly:,.2f}\n")
            else:
                output_buffer.write(f"  Basic Monthly Cash Flow (Total Rent - PITI): -${abs(simple_cash_flow_monthly):,.2f} (Loss)\n")

            if monthly_piti > 0:
                rent_to_piti_multiple = total_monthly_pha_rent / monthly_piti
                output_buffer.write(f"  Rent to PITI Multiple: {rent_to_piti_multiple:.2f}x\n")
            elif total_monthly_pha_rent > 0 and monthly_piti == 0:
                output_buffer.write(f"  Rent to PITI Multiple: Infinite (PITI is $0, Rent > $0)\n")
            else:
                output_buffer.write(f"  Rent to PITI Multiple: N/A\n")
            output_buffer.write("-" * 50 + "\n")

            output_buffer.write("Annual Operating Income & Expenses:\n")
            gpr_annual = total_monthly_pha_rent * 12
            output_buffer.write(f"  Gross Potential Rent (GPR): ${gpr_annual:,.2f}\n")
            output_buffer.write(f"  Vacancy Allowance ({vac_rate}% of GPR): -${summary.get('vacancy_allowance_annual', 0.0):,.2f}\n")
            output_buffer.write(f"  Effective Gross Income (EGI): ${summary.get('effective_gross_income_annual', 0.0):,.2f}\n")
            output_buffer.write("  Operating Expenses (Annual):\n")
            output_buffer.write(f"    Property Taxes: ${float(annual_taxes):,.2f}\n")
            output_buffer.write(f"    Property Insurance: ${float(annual_insurance):,.2f}\n")
            output_buffer.write(f"    Repairs & Maintenance ({rep_maint_percent}% of GPR): ${summary.get('repairs_allowance_annual', 0.0):,.2f}\n")
            output_buffer.write(f"    Property Management ({prop_mgmt_percent}% of GPR): ${summary.get('management_fee_annual', 0.0):,.2f}\n")
            output_buffer.write(f"    Other Operating Expenses: ${float(other_opex):,.2f}\n")
            output_buffer.write(f"  Net Operating Income (NOI): ${summary.get('noi_annual', 0.0):,.2f}\n")
            output_buffer.write("-" * 50 + "\n")

            output_buffer.write("Cash Flow & Returns (Comprehensive):\n")
            output_buffer.write(f"  Annual Debt Service (P&I): ${summary.get('annual_debt_service', 0.0):,.2f}\n")
            output_buffer.write(f"  Comprehensive Cash Flow Before Tax (Annual - CFBT): ${summary.get('cash_flow_before_tax_annual', 0.0):,.2f}\n")
            output_buffer.write(f"  Comprehensive Cash Flow Before Tax (Monthly - CFBT): ${summary.get('cash_flow_before_tax_monthly', 0.0):,.2f}\n")

            coc = summary.get('cash_on_cash_return_percent', 0.0)
            if coc == float('inf'):
                output_buffer.write(f"  Cash-on-Cash Return: Infinite\n")
            elif coc == -float('inf'):
                 output_buffer.write(f"  Cash-on-Cash Return: N/A (Negative CF on $0 Down or $0 Investment with Negative CF)\n")
            else:
                output_buffer.write(f"  Cash-on-Cash Return: {coc:.2f}%\n")

            cap_rate = summary.get('cap_rate_percent', 0.0)
            if cap_rate == float('inf'):
                output_buffer.write(f"  Capitalization Rate (Cap Rate): Infinite (NOI > 0, Price = $0)\n")
            else:
                output_buffer.write(f"  Capitalization Rate (Cap Rate): {cap_rate:.2f}%\n")
            output_buffer.write(f"  Gross Rent Multiplier (GRM): {summary.get('grm', 0.0):.2f}\n")
            output_buffer.write("-" * 50 + "\n")

            output_buffer.write("Longer-Term Projections (Simplified):\n")
            output_buffer.write(f"  Gross Potential Revenue (5 Years): ${summary.get('gross_revenue_5_years', 0.0):,.2f}\n")
            output_buffer.write(f"  Est. Net Operating Income (NOI, 5 Years): ${summary.get('noi_5_years', 0.0):,.2f}\n")
            output_buffer.write("-" * 50 + "\n")

        except KeyError as e:
            output_buffer.write(f"🚨 INTERNAL DISPLAY ERROR: A required key is missing in the results: {e}\n")
            output_buffer.write(f"Full 'analysis_results' dictionary for debugging: {analysis_results}\n")
        except Exception as e:
            output_buffer.write(f"🚨 AN UNEXPECTED ERROR occurred during result display: {e}\n")
            import traceback
            output_buffer.write(traceback.format_exc() + "\n")

    results_string = output_buffer.getvalue()
    output_buffer.close()
    return results_string
