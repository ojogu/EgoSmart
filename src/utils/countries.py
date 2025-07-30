def get_country_by_dial_code(dial_code):
    """
    Look up country details by dial code (without the + sign).
    
    Args:
        dial_code (str or int): The country dial code (e.g., "234" or 234 for Nigeria)
    
    Returns:
        dict or None: Country details if found, None if not found
    """
    
    # Country data
    countries = [
        {"country_name": "Afghanistan", "country_code": "AF", "country_dial_code": "+93", "country_flag": "🇦🇫"},
        {"country_name": "Albania", "country_code": "AL", "country_dial_code": "+355", "country_flag": "🇦🇱"},
        {"country_name": "Algeria", "country_code": "DZ", "country_dial_code": "+213", "country_flag": "🇩🇿"},
        {"country_name": "American Samoa", "country_code": "AS", "country_dial_code": "+1-684", "country_flag": "🇦🇸"},
        {"country_name": "Andorra", "country_code": "AD", "country_dial_code": "+376", "country_flag": "🇦🇩"},
        {"country_name": "Angola", "country_code": "AO", "country_dial_code": "+244", "country_flag": "🇦🇴"},
        {"country_name": "Anguilla", "country_code": "AI", "country_dial_code": "+1-264", "country_flag": "🇦🇮"},
        {"country_name": "Antigua and Barbuda", "country_code": "AG", "country_dial_code": "+1-268", "country_flag": "🇦🇬"},
        {"country_name": "Argentina", "country_code": "AR", "country_dial_code": "+54", "country_flag": "🇦🇷"},
        {"country_name": "Armenia", "country_code": "AM", "country_dial_code": "+374", "country_flag": "🇦🇲"},
        {"country_name": "Aruba", "country_code": "AW", "country_dial_code": "+297", "country_flag": "🇦🇼"},
        {"country_name": "Australia", "country_code": "AU", "country_dial_code": "+61", "country_flag": "🇦🇺"},
        {"country_name": "Austria", "country_code": "AT", "country_dial_code": "+43", "country_flag": "🇦🇹"},
        {"country_name": "Azerbaijan", "country_code": "AZ", "country_dial_code": "+994", "country_flag": "🇦🇿"},
        {"country_name": "Bahamas", "country_code": "BS", "country_dial_code": "+1-242", "country_flag": "🇧🇸"},
        {"country_name": "Bahrain", "country_code": "BH", "country_dial_code": "+973", "country_flag": "🇧🇭"},
        {"country_name": "Bangladesh", "country_code": "BD", "country_dial_code": "+880", "country_flag": "🇧🇩"},
        {"country_name": "Barbados", "country_code": "BB", "country_dial_code": "+1-246", "country_flag": "🇧🇧"},
        {"country_name": "Belarus", "country_code": "BY", "country_dial_code": "+375", "country_flag": "🇧🇾"},
        {"country_name": "Belgium", "country_code": "BE", "country_dial_code": "+32", "country_flag": "🇧🇪"},
        {"country_name": "Belize", "country_code": "BZ", "country_dial_code": "+501", "country_flag": "🇧🇿"},
        {"country_name": "Benin", "country_code": "BJ", "country_dial_code": "+229", "country_flag": "🇧🇯"},
        {"country_name": "Bermuda", "country_code": "BM", "country_dial_code": "+1-441", "country_flag": "🇧🇲"},
        {"country_name": "Bhutan", "country_code": "BT", "country_dial_code": "+975", "country_flag": "🇧🇹"},
        {"country_name": "Bolivia, Plurinational State of", "country_code": "BO", "country_dial_code": "+591", "country_flag": "🇧🇴"},
        {"country_name": "Bosnia and Herzegovina", "country_code": "BA", "country_dial_code": "+387", "country_flag": "🇧🇦"},
        {"country_name": "Botswana", "country_code": "BW", "country_dial_code": "+267", "country_flag": "🇧🇼"},
        {"country_name": "Brazil", "country_code": "BR", "country_dial_code": "+55", "country_flag": "🇧🇷"},
        {"country_name": "Brunei Darussalam", "country_code": "BN", "country_dial_code": "+673", "country_flag": "🇧🇳"},
        {"country_name": "Bulgaria", "country_code": "BG", "country_dial_code": "+359", "country_flag": "🇧🇬"},
        {"country_name": "Burkina Faso", "country_code": "BF", "country_dial_code": "+226", "country_flag": "🇧🇫"},
        {"country_name": "Burundi", "country_code": "BI", "country_dial_code": "+257", "country_flag": "🇧🇮"},
        {"country_name": "Cabo Verde", "country_code": "CV", "country_dial_code": "+238", "country_flag": "🇨🇻"},
        {"country_name": "Cambodia", "country_code": "KH", "country_dial_code": "+855", "country_flag": "🇰🇭"},
        {"country_name": "Cameroon", "country_code": "CM", "country_dial_code": "+237", "country_flag": "🇨🇲"},
        {"country_name": "Canada", "country_code": "CA", "country_dial_code": "+1", "country_flag": "🇨🇦"},
        {"country_name": "Central African Republic", "country_code": "CF", "country_dial_code": "+236", "country_flag": "🇨🇫"},
        {"country_name": "Chad", "country_code": "TD", "country_dial_code": "+235", "country_flag": "🇹🇩"},
        {"country_name": "Chile", "country_code": "CL", "country_dial_code": "+56", "country_flag": "🇨🇱"},
        {"country_name": "China", "country_code": "CN", "country_dial_code": "+86", "country_flag": "🇨🇳"},
        {"country_name": "Colombia", "country_code": "CO", "country_dial_code": "+57", "country_flag": "🇨🇴"},
        {"country_name": "Comoros", "country_code": "KM", "country_dial_code": "+269", "country_flag": "🇰🇲"},
        {"country_name": "Congo", "country_code": "CG", "country_dial_code": "+242", "country_flag": "🇨🇬"},
        {"country_name": "Congo, The Democratic Republic of the", "country_code": "CD", "country_dial_code": "+243", "country_flag": "🇨🇩"},
        {"country_name": "Costa Rica", "country_code": "CR", "country_dial_code": "+506", "country_flag": "🇨🇷"},
        {"country_name": "Croatia", "country_code": "HR", "country_dial_code": "+385", "country_flag": "🇭🇷"},
        {"country_name": "Cuba", "country_code": "CU", "country_dial_code": "+53", "country_flag": "🇨🇺"},
        {"country_name": "Cyprus", "country_code": "CY", "country_dial_code": "+357", "country_flag": "🇨🇾"},
        {"country_name": "Czechia", "country_code": "CZ", "country_dial_code": "+420", "country_flag": "🇨🇿"},
        {"country_name": "Côte d'Ivoire", "country_code": "CI", "country_dial_code": "+225", "country_flag": "🇨🇮"},
        {"country_name": "Denmark", "country_code": "DK", "country_dial_code": "+45", "country_flag": "🇩🇰"},
        {"country_name": "Djibouti", "country_code": "DJ", "country_dial_code": "+253", "country_flag": "🇩🇯"},
        {"country_name": "Dominica", "country_code": "DM", "country_dial_code": "+1-767", "country_flag": "🇩🇲"},
        {"country_name": "Dominican Republic", "country_code": "DO", "country_dial_code": "+1-809", "country_flag": "🇩🇴"},
        {"country_name": "Ecuador", "country_code": "EC", "country_dial_code": "+593", "country_flag": "🇪🇨"},
        {"country_name": "Egypt", "country_code": "EG", "country_dial_code": "+20", "country_flag": "🇪🇬"},
        {"country_name": "El Salvador", "country_code": "SV", "country_dial_code": "+503", "country_flag": "🇸🇻"},
        {"country_name": "Equatorial Guinea", "country_code": "GQ", "country_dial_code": "+240", "country_flag": "🇬🇶"},
        {"country_name": "Eritrea", "country_code": "ER", "country_dial_code": "+291", "country_flag": "🇪🇷"},
        {"country_name": "Estonia", "country_code": "EE", "country_dial_code": "+372", "country_flag": "🇪🇪"},
        {"country_name": "Eswatini", "country_code": "SZ", "country_dial_code": "+268", "country_flag": "🇸🇿"},
        {"country_name": "Ethiopia", "country_code": "ET", "country_dial_code": "+251", "country_flag": "🇪🇹"},
        {"country_name": "Fiji", "country_code": "FJ", "country_dial_code": "+679", "country_flag": "🇫🇯"},
        {"country_name": "Finland", "country_code": "FI", "country_dial_code": "+358", "country_flag": "🇫🇮"},
        {"country_name": "France", "country_code": "FR", "country_dial_code": "+33", "country_flag": "🇫🇷"},
        {"country_name": "Gabon", "country_code": "GA", "country_dial_code": "+241", "country_flag": "🇬🇦"},
        {"country_name": "Gambia", "country_code": "GM", "country_dial_code": "+220", "country_flag": "🇬🇲"},
        {"country_name": "Georgia", "country_code": "GE", "country_dial_code": "+995", "country_flag": "🇬🇪"},
        {"country_name": "Germany", "country_code": "DE", "country_dial_code": "+49", "country_flag": "🇩🇪"},
        {"country_name": "Ghana", "country_code": "GH", "country_dial_code": "+233", "country_flag": "🇬🇭"},
        {"country_name": "Greece", "country_code": "GR", "country_dial_code": "+30", "country_flag": "🇬🇷"},
        {"country_name": "Grenada", "country_code": "GD", "country_dial_code": "+1-473", "country_flag": "🇬🇩"},
        {"country_name": "Guatemala", "country_code": "GT", "country_dial_code": "+502", "country_flag": "🇬🇹"},
        {"country_name": "Guinea", "country_code": "GN", "country_dial_code": "+224", "country_flag": "🇬🇳"},
        {"country_name": "Guinea-Bissau", "country_code": "GW", "country_dial_code": "+245", "country_flag": "🇬🇼"},
        {"country_name": "Guyana", "country_code": "GY", "country_dial_code": "+592", "country_flag": "🇬🇾"},
        {"country_name": "Haiti", "country_code": "HT", "country_dial_code": "+509", "country_flag": "🇭🇹"},
        {"country_name": "Honduras", "country_code": "HN", "country_dial_code": "+504", "country_flag": "🇭🇳"},
        {"country_name": "Hong Kong", "country_code": "HK", "country_dial_code": "+852", "country_flag": "🇭🇰"},
        {"country_name": "Hungary", "country_code": "HU", "country_dial_code": "+36", "country_flag": "🇭🇺"},
        {"country_name": "Iceland", "country_code": "IS", "country_dial_code": "+354", "country_flag": "🇮🇸"},
        {"country_name": "India", "country_code": "IN", "country_dial_code": "+91", "country_flag": "🇮🇳"},
        {"country_name": "Indonesia", "country_code": "ID", "country_dial_code": "+62", "country_flag": "🇮🇩"},
        {"country_name": "Iran, Islamic Republic of", "country_code": "IR", "country_dial_code": "+98", "country_flag": "🇮🇷"},
        {"country_name": "Iraq", "country_code": "IQ", "country_dial_code": "+964", "country_flag": "🇮🇶"},
        {"country_name": "Ireland", "country_code": "IE", "country_dial_code": "+353", "country_flag": "🇮🇪"},
        {"country_name": "Israel", "country_code": "IL", "country_dial_code": "+972", "country_flag": "🇮🇱"},
        {"country_name": "Italy", "country_code": "IT", "country_dial_code": "+39", "country_flag": "🇮🇹"},
        {"country_name": "Jamaica", "country_code": "JM", "country_dial_code": "+1-876", "country_flag": "🇯🇲"},
        {"country_name": "Japan", "country_code": "JP", "country_dial_code": "+81", "country_flag": "🇯🇵"},
        {"country_name": "Jordan", "country_code": "JO", "country_dial_code": "+962", "country_flag": "🇯🇴"},
        {"country_name": "Kazakhstan", "country_code": "KZ", "country_dial_code": "+7", "country_flag": "🇰🇿"},
        {"country_name": "Kenya", "country_code": "KE", "country_dial_code": "+254", "country_flag": "🇰🇪"},
        {"country_name": "Kiribati", "country_code": "KI", "country_dial_code": "+686", "country_flag": "🇰🇮"},
        {"country_name": "Korea, Democratic People's Republic of", "country_code": "KP", "country_dial_code": "+850", "country_flag": "🇰🇵"},
        {"country_name": "Korea, Republic of", "country_code": "KR", "country_dial_code": "+82", "country_flag": "🇰🇷"},
        {"country_name": "Kuwait", "country_code": "KW", "country_dial_code": "+965", "country_flag": "🇰🇼"},
        {"country_name": "Kyrgyzstan", "country_code": "KG", "country_dial_code": "+996", "country_flag": "🇰🇬"},
        {"country_name": "Lao People's Democratic Republic", "country_code": "LA", "country_dial_code": "+856", "country_flag": "🇱🇦"},
        {"country_name": "Latvia", "country_code": "LV", "country_dial_code": "+371", "country_flag": "🇱🇻"},
        {"country_name": "Lebanon", "country_code": "LB", "country_dial_code": "+961", "country_flag": "🇱🇧"},
        {"country_name": "Lesotho", "country_code": "LS", "country_dial_code": "+266", "country_flag": "🇱🇸"},
        {"country_name": "Liberia", "country_code": "LR", "country_dial_code": "+231", "country_flag": "🇱🇷"},
        {"country_name": "Libya", "country_code": "LY", "country_dial_code": "+218", "country_flag": "🇱🇾"},
        {"country_name": "Liechtenstein", "country_code": "LI", "country_dial_code": "+423", "country_flag": "🇱🇮"},
        {"country_name": "Lithuania", "country_code": "LT", "country_dial_code": "+370", "country_flag": "🇱🇹"},
        {"country_name": "Luxembourg", "country_code": "LU", "country_dial_code": "+352", "country_flag": "🇱🇺"},
        {"country_name": "Macao", "country_code": "MO", "country_dial_code": "+853", "country_flag": "🇲🇴"},
        {"country_name": "Madagascar", "country_code": "MG", "country_dial_code": "+261", "country_flag": "🇲🇬"},
        {"country_name": "Malawi", "country_code": "MW", "country_dial_code": "+265", "country_flag": "🇲🇼"},
        {"country_name": "Malaysia", "country_code": "MY", "country_dial_code": "+60", "country_flag": "🇲🇾"},
        {"country_name": "Maldives", "country_code": "MV", "country_dial_code": "+960", "country_flag": "🇲🇻"},
        {"country_name": "Mali", "country_code": "ML", "country_dial_code": "+223", "country_flag": "🇲🇱"},
        {"country_name": "Malta", "country_code": "MT", "country_dial_code": "+356", "country_flag": "🇲🇹"},
        {"country_name": "Marshall Islands", "country_code": "MH", "country_dial_code": "+692", "country_flag": "🇲🇭"},
        {"country_name": "Mauritania", "country_code": "MR", "country_dial_code": "+222", "country_flag": "🇲🇷"},
        {"country_name": "Mauritius", "country_code": "MU", "country_dial_code": "+230", "country_flag": "🇲🇺"},
        {"country_name": "Mexico", "country_code": "MX", "country_dial_code": "+52", "country_flag": "🇲🇽"},
        {"country_name": "Micronesia, Federated States of", "country_code": "FM", "country_dial_code": "+691", "country_flag": "🇫🇲"},
        {"country_name": "Moldova, Republic of", "country_code": "MD", "country_dial_code": "+373", "country_flag": "🇲🇩"},
        {"country_name": "Monaco", "country_code": "MC", "country_dial_code": "+377", "country_flag": "🇲🇨"},
        {"country_name": "Mongolia", "country_code": "MN", "country_dial_code": "+976", "country_flag": "🇲🇳"},
        {"country_name": "Montenegro", "country_code": "ME", "country_dial_code": "+382", "country_flag": "🇲🇪"},
        {"country_name": "Morocco", "country_code": "MA", "country_dial_code": "+212", "country_flag": "🇲🇦"},
        {"country_name": "Mozambique", "country_code": "MZ", "country_dial_code": "+258", "country_flag": "🇲🇿"},
        {"country_name": "Myanmar", "country_code": "MM", "country_dial_code": "+95", "country_flag": "🇲🇲"},
        {"country_name": "Namibia", "country_code": "NA", "country_dial_code": "+264", "country_flag": "🇳🇦"},
        {"country_name": "Nauru", "country_code": "NR", "country_dial_code": "+674", "country_flag": "🇳🇷"},
        {"country_name": "Nepal", "country_code": "NP", "country_dial_code": "+977", "country_flag": "🇳🇵"},
        {"country_name": "Netherlands", "country_code": "NL", "country_dial_code": "+31", "country_flag": "🇳🇱"},
        {"country_name": "New Zealand", "country_code": "NZ", "country_dial_code": "+64", "country_flag": "🇳🇿"},
        {"country_name": "Nicaragua", "country_code": "NI", "country_dial_code": "+505", "country_flag": "🇳🇮"},
        {"country_name": "Niger", "country_code": "NE", "country_dial_code": "+227", "country_flag": "🇳🇪"},
        {"country_name": "Nigeria", "country_code": "NG", "country_dial_code": "+234", "country_flag": "🇳🇬"},
        {"country_name": "North Macedonia", "country_code": "MK", "country_dial_code": "+389", "country_flag": "🇲🇰"},
        {"country_name": "Norway", "country_code": "NO", "country_dial_code": "+47", "country_flag": "🇳🇴"},
        {"country_name": "Oman", "country_code": "OM", "country_dial_code": "+968", "country_flag": "🇴🇲"},
        {"country_name": "Pakistan", "country_code": "PK", "country_dial_code": "+92", "country_flag": "🇵🇰"},
        {"country_name": "Palau", "country_code": "PW", "country_dial_code": "+680", "country_flag": "🇵🇼"},
        {"country_name": "Panama", "country_code": "PA", "country_dial_code": "+507", "country_flag": "🇵🇦"},
        {"country_name": "Papua New Guinea", "country_code": "PG", "country_dial_code": "+675", "country_flag": "🇵🇬"},
        {"country_name": "Paraguay", "country_code": "PY", "country_dial_code": "+595", "country_flag": "🇵🇾"},
        {"country_name": "Peru", "country_code": "PE", "country_dial_code": "+51", "country_flag": "🇵🇪"},
        {"country_name": "Philippines", "country_code": "PH", "country_dial_code": "+63", "country_flag": "🇵🇭"},
        {"country_name": "Poland", "country_code": "PL", "country_dial_code": "+48", "country_flag": "🇵🇱"},
        {"country_name": "Portugal", "country_code": "PT", "country_dial_code": "+351", "country_flag": "🇵🇹"},
        {"country_name": "Qatar", "country_code": "QA", "country_dial_code": "+974", "country_flag": "🇶🇦"},
        {"country_name": "Romania", "country_code": "RO", "country_dial_code": "+40", "country_flag": "🇷🇴"},
        {"country_name": "Russian Federation", "country_code": "RU", "country_dial_code": "+7", "country_flag": "🇷🇺"},
        {"country_name": "Rwanda", "country_code": "RW", "country_dial_code": "+250", "country_flag": "🇷🇼"},
        {"country_name": "Saint Kitts and Nevis", "country_code": "KN", "country_dial_code": "+1-869", "country_flag": "🇰🇳"},
        {"country_name": "Saint Lucia", "country_code": "LC", "country_dial_code": "+1-758", "country_flag": "🇱🇨"},
        {"country_name": "Saint Vincent and the Grenadines", "country_code": "VC", "country_dial_code": "+1-784", "country_flag": "🇻🇨"},
        {"country_name": "Samoa", "country_code": "WS", "country_dial_code": "+685", "country_flag": "🇼🇸"},
        {"country_name": "San Marino", "country_code": "SM", "country_dial_code": "+378", "country_flag": "🇸🇲"},
        {"country_name": "Sao Tome and Principe", "country_code": "ST", "country_dial_code": "+239", "country_flag": "🇸🇹"},
        {"country_name": "Saudi Arabia", "country_code": "SA", "country_dial_code": "+966", "country_flag": "🇸🇦"},
        {"country_name": "Senegal", "country_code": "SN", "country_dial_code": "+221", "country_flag": "🇸🇳"},
        {"country_name": "Serbia", "country_code": "RS", "country_dial_code": "+381", "country_flag": "🇷🇸"},
        {"country_name": "Seychelles", "country_code": "SC", "country_dial_code": "+248", "country_flag": "🇸🇨"},
        {"country_name": "Sierra Leone", "country_code": "SL", "country_dial_code": "+232", "country_flag": "🇸🇱"},
        {"country_name": "Singapore", "country_code": "SG", "country_dial_code": "+65", "country_flag": "🇸🇬"},
        {"country_name": "Slovakia", "country_code": "SK", "country_dial_code": "+421", "country_flag": "🇸🇰"},
        {"country_name": "Slovenia", "country_code": "SI", "country_dial_code": "+386", "country_flag": "🇸🇮"},
        {"country_name": "Solomon Islands", "country_code": "SB", "country_dial_code": "+677", "country_flag": "🇸🇧"},
        {"country_name": "Somalia", "country_code": "SO", "country_dial_code": "+252", "country_flag": "🇸🇴"},
        {"country_name": "South Africa", "country_code": "ZA", "country_dial_code": "+27", "country_flag": "🇿🇦"},
        {"country_name": "South Sudan", "country_code": "SS", "country_dial_code": "+211", "country_flag": "🇸🇸"},
        {"country_name": "Spain", "country_code": "ES", "country_dial_code": "+34", "country_flag": "🇪🇸"},
        {"country_name": "Sri Lanka", "country_code": "LK", "country_dial_code": "+94", "country_flag": "🇱🇰"},
        {"country_name": "Sudan", "country_code": "SD", "country_dial_code": "+249", "country_flag": "🇸🇩"},
        {"country_name": "Suriname", "country_code": "SR", "country_dial_code": "+597", "country_flag": "🇸🇷"},
        {"country_name": "Sweden", "country_code": "SE", "country_dial_code": "+46", "country_flag": "🇸🇪"},
        {"country_name": "Switzerland", "country_code": "CH", "country_dial_code": "+41", "country_flag": "🇨🇭"},
        {"country_name": "Syrian Arab Republic", "country_code": "SY", "country_dial_code": "+963", "country_flag": "🇸🇾"},
        {"country_name": "Taiwan, Province of China", "country_code": "TW", "country_dial_code": "+886", "country_flag": "🇹🇼"},
        {"country_name": "Tajikistan", "country_code": "TJ", "country_dial_code": "+992", "country_flag": "🇹🇯"},
        {"country_name": "Tanzania, United Republic of", "country_code": "TZ", "country_dial_code": "+255", "country_flag": "🇹🇿"},
        {"country_name": "Thailand", "country_code": "TH", "country_dial_code": "+66", "country_flag": "🇹🇭"},
        {"country_name": "Timor-Leste", "country_code": "TL", "country_dial_code": "+670", "country_flag": "🇹🇱"},
        {"country_name": "Togo", "country_code": "TG", "country_dial_code": "+228", "country_flag": "🇹🇬"},
        {"country_name": "Tonga", "country_code": "TO", "country_dial_code": "+676", "country_flag": "🇹🇴"},
        {"country_name": "Trinidad and Tobago", "country_code": "TT", "country_dial_code": "+1-868", "country_flag": "🇹🇹"},
        {"country_name": "Tunisia", "country_code": "TN", "country_dial_code": "+216", "country_flag": "🇹🇳"},
        {"country_name": "Turkey", "country_code": "TR", "country_dial_code": "+90", "country_flag": "🇹🇷"},
        {"country_name": "Turkmenistan", "country_code": "TM", "country_dial_code": "+993", "country_flag": "🇹🇲"},
        {"country_name": "Tuvalu", "country_code": "TV", "country_dial_code": "+688", "country_flag": "🇹🇻"},
        {"country_name": "Uganda", "country_code": "UG", "country_dial_code": "+256", "country_flag": "🇺🇬"},
        {"country_name": "Ukraine", "country_code": "UA", "country_dial_code": "+380", "country_flag": "🇺🇦"},
        {"country_name": "United Arab Emirates", "country_code": "AE", "country_dial_code": "+971", "country_flag": "🇦🇪"},
        {"country_name": "United Kingdom", "country_code": "GB", "country_dial_code": "+44", "country_flag": "🇬🇧"},
        {"country_name": "United States", "country_code": "US", "country_dial_code": "+1", "country_flag": "🇺🇸"},
        {"country_name": "Uruguay", "country_code": "UY", "country_dial_code": "+598", "country_flag": "🇺🇾"},
        {"country_name": "Uzbekistan", "country_code": "UZ", "country_dial_code": "+998", "country_flag": "🇺🇿"},
        {"country_name": "Vanuatu", "country_code": "VU", "country_dial_code": "+678", "country_flag": "🇻🇺"},
        {"country_name": "Venezuela, Bolivarian Republic of", "country_code": "VE", "country_dial_code": "+58", "country_flag": "🇻🇪"},
        {"country_name": "Viet Nam", "country_code": "VN", "country_dial_code": "+84", "country_flag": "🇻🇳"},
        {"country_name": "Yemen", "country_code": "YE", "country_dial_code": "+967", "country_flag": "🇾🇪"},
        {"country_name": "Zambia", "country_code": "ZM", "country_dial_code": "+260", "country_flag": "🇿🇲"},
        {"country_name": "Zimbabwe", "country_code": "ZW", "country_dial_code": "+263", "country_flag": "🇿🇼"}
    ]
    # Convert input to string and handle different formats
    dial_code = str(dial_code).strip()
    
    # Remove + if present
    if dial_code.startswith('+'):
        dial_code = dial_code[1:]
    
    # Search for the country by dial code
    for country in countries:
        # Extract the numeric part from the dial code (remove + and any extensions)
        country_dial = country["country_dial_code"].replace("+", "").split("-")[0]
        
        # Check for exact match or if input matches the base country code
        if dial_code == country_dial or dial_code == country["country_dial_code"].replace("+", ""):
            return country
    
    # Return None if no match found
    return None


# Example usage and test function
def test_function():
    """Test the function with some examples"""
    
    # Test with Nigeria (234)
    result = get_country_by_dial_code("234")
    print(f"Dial code 234: {result}")
    
    # Test with US (1)
    result = get_country_by_dial_code(1)
    print(f"Dial code 1: {result}")
    
    # Test with UK (44)
    result = get_country_by_dial_code("44")
    print(f"Dial code 44: {result}")
    
    # Test with invalid code
    result = get_country_by_dial_code("999")
    print(f"Dial code 999: {result}")


# Run the test
if __name__ == "__main__":
    test_function()