# Philadelphia Multifamily Property Analyzer 🏢

A comprehensive web application for analyzing multifamily real estate investments in Philadelphia using official PHA (Philadelphia Housing Authority) payment standards.

## Features ✨

- **PHA Payment Standards Integration**: Uses official Philadelphia Housing Authority rent standards by ZIP code
- **Comprehensive Financial Analysis**: Cap rates, cash-on-cash returns, NOI, cash flow projections
- **Unit Mix Flexibility**: Support for various unit configurations (SRO, 0-8 bedrooms)
- **Neighborhood Mapping**: Client-friendly neighborhood names for all Philadelphia ZIP codes
- **PDF Report Generation**: Professional downloadable reports
- **Interactive Charts**: Visual representation of key metrics
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices

## Live Demo 🌐

**[Try the live application here](https://your-app-url.streamlit.app)** *(URL will be available after deployment)*

## How to Use 📋

1. **Select ZIP Code**: Choose your property's Philadelphia ZIP code
2. **Configure Units**: Enter unit mix using formats like:
   - `5x1BR, 3x2BR, 2x3BR` (5 one-bedrooms, 3 two-bedrooms, 2 three-bedrooms)
   - `1,2,3,1,1` (individual unit listing)
3. **Enter Financial Details**: Property price, down payment, interest rate, etc.
4. **Set Operating Expenses**: Vacancy rate, maintenance, management percentages
5. **Analyze**: Get comprehensive investment analysis with key metrics

## PHA Groups & Rent Types 🏘️

Philadelphia properties are categorized into 4 PHA groups based on location:

- **Group 1**: Traditional Rents (Lower rent areas)
- **Group 2**: Mid-Range Rents 
- **Group 3**: Opportunity Rents
- **Group 4**: High-Opportunity Rents (Higher rent areas like Center City)

## Key Metrics Calculated 📊

- **Monthly Cash Flow**: Net monthly income after all expenses and debt service
- **Cap Rate**: Net Operating Income / Property Price
- **Cash-on-Cash Return**: Annual cash flow / Initial cash investment
- **Gross Rent Multiplier (GRM)**: Property price / Annual gross rent
- **PITI Breakdown**: Principal, Interest, Taxes, Insurance
- **Net Operating Income (NOI)**: Income after operating expenses, before debt service
- **Rent-to-PITI Ratio**: Total rent compared to mortgage payment

## Installation & Local Development 🛠️

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Local Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/philly-multifamily-calculator.git
   cd philly-multifamily-calculator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Open in browser**: The app will automatically open at `http://localhost:8501`

## Deployment 🚀

### Streamlit Cloud (Recommended)
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy with one click!

### Alternative Deployment Options
- **Heroku**: Use the included `Procfile`
- **Railway**: Direct GitHub integration
- **DigitalOcean App Platform**: Container deployment
- **AWS/GCP/Azure**: Container or serverless deployment

## File Structure 📁

```
philly-multifamily-calculator/
├── streamlit_app.py          # Main Streamlit application
├── calculator.py             # Core calculation functions and data
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── .streamlit/              # Streamlit configuration (optional)
│   └── config.toml
└── assets/                  # Additional assets (optional)
    └── logo.png
```

## Data Sources 📈

- **PHA Payment Standards**: Philadelphia Housing Authority SAFMR data (effective October 1, 2024)
- **ZIP Code Groupings**: Official PHA rent group classifications
- **Neighborhood Mapping**: Custom mapping of ZIP codes to client-friendly neighborhood names

## Contributing 🤝

Contributions are welcome! Here's how you can help:

1. **Report Issues**: Found a bug? Report it in the Issues section
2. **Suggest Features**: Have ideas for improvements? Create a feature request
3. **Submit Pull Requests**: 
   - Fork the repository
   - Create a feature branch (`git checkout -b feature/AmazingFeature`)
   - Commit your changes (`git commit -m 'Add some AmazingFeature'`)
   - Push to the branch (`git push origin feature/AmazingFeature`)
   - Open a Pull Request

## Roadmap 🗺️

### Planned Features
- [ ] Market comparison data integration
- [ ] Sensitivity analysis tools
- [ ] Multi-year projection modeling
- [ ] Portfolio analysis capabilities
- [ ] Integration with MLS data
- [ ] Mobile app version
- [ ] User accounts and saved analyses

### Potential Integrations
- [ ] Zillow API for property values
- [ ] Census data for demographic information
- [ ] Crime statistics overlay
- [ ] School district information
- [ ] Transit accessibility scores

## Technical Details 🔧

### Built With
- **Streamlit**: Web application framework
- **Python**: Core programming language
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive charts and visualizations
- **ReportLab/xhtml2pdf**: PDF report generation

### Key Functions
- `analyze_multifamily_property()`: Main analysis engine
- `get_pha_payment_standard()`: PHA rent lookup
- `calculate_monthly_piti()`: Mortgage payment calculation
- `get_client_friendly_neighborhood()`: ZIP to neighborhood mapping

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer ⚠️

This tool is for educational and informational purposes only. Always consult with qualified real estate professionals, accountants, and attorneys before making investment decisions. The PHA payment standards and calculations provided are based on publicly available data and should be verified independently.

## Support & Contact 📞

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Questions**: Start a Discussion on GitHub
- **Email**: [your-email@example.com](mailto:your-email@example.com)

## Acknowledgments 🙏

- Philadelphia Housing Authority for providing public payment standard data
- Streamlit team for the excellent web app framework
- Philadelphia real estate community for feedback and testing

---

**Made with ❤️ for the Philadelphia real estate investment community**

## Quick Links 🔗

- [Live Application](https://your-app-url.streamlit.app)
- [GitHub Repository](https://github.com/yourusername/philly-multifamily-calculator)
- [Report Issues](https://github.com/yourusername/philly-multifamily-calculator/issues)
- [Philadelphia Housing Authority](https://www.pha.phila.gov/)

## Example Analysis Output

```
--- MULTIFAMILY CALCULATION RESULTS ---
Input Unit String: 5x1BR, 3x2BR, 2x3BR
Property ZIP Code: 19121
Client-Friendly Area: Temple University Area / Lower North Philly

Unit Breakdown (Potential PHA Rents) - Total 10 units processed:
  Unit 1 (Input: '1BR', Type: Mid Range Rents): $1,540.00/mo (Group 2)
  Unit 2 (Input: '1BR', Type: Mid Range Rents): $1,540.00/mo (Group 2)
  ...
  Total Potential Monthly PHA Rent: $18,450.00

Property Financial Summary:
  Acquisition Price: $500,000.00
  Down Payment (25%): $125,000.00

Monthly Cash Flow: $2,847.33
Cap Rate: 8.2%
Cash-on-Cash Return: 22.5%
```