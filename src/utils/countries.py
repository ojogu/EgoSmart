import phonenumbers
from phonenumbers import geocoder, carrier, NumberParseException
from typing import Optional, Dict, Any


def parse_number(phone: str, default_region: Optional[str] = None) -> Dict[str, Any]:
    """
    Parse and extract information from a phone number.
    
    Args:
        phone: Phone number string (with or without + prefix)
        default_region: ISO 3166-1 alpha-2 country code (e.g., 'US', 'NG')
                       Used when phone number doesn't have country code
    
    Returns:
        Dictionary containing phone number details
        
    Raises:
        ValueError: If the phone number is invalid or cannot be parsed
    """
    if not phone:
        raise ValueError("Phone number cannot be empty")
    
    # Remove whitespace
    phone = phone.strip()
    
    # Add + prefix if not present and phone starts with digits
    if phone and phone[0].isdigit():
        phone = "+" + phone
    
    try:
        number = phonenumbers.parse(phone, default_region)
        
        # Validate the number
        if not phonenumbers.is_valid_number(number):
            raise ValueError(f"Invalid phone number: {phone}")
        
        return {
            "country_code": number.country_code,
            "national_number": number.national_number,
            "country_name": geocoder.description_for_number(number, "en") or "Unknown",
            "carrier": carrier.name_for_number(number, "en") or "Unknown",
            "is_valid": True,
            "is_possible": phonenumbers.is_possible_number(number),
            "formatted_international": phonenumbers.format_number(
                number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            ),
            "formatted_national": phonenumbers.format_number(
                number, phonenumbers.PhoneNumberFormat.NATIONAL
            ),
            "formatted_e164": phonenumbers.format_number(
                number, phonenumbers.PhoneNumberFormat.E164
            )
        }
        
    except NumberParseException as e:
        raise ValueError(f"Failed to parse phone number '{phone}': {e}")
    except Exception as e:
        raise ValueError(f"Unexpected error parsing phone number: {e}")


# Example usage with error handling
# if __name__ == "__main__":
#     test_numbers = [
#         "2349065011334",
#         "+2348123456789",
#         "+14155552671",
#         "invalid_number"
#     ]
    
#     for num in test_numbers:
#         try:
#             result = parse_number(num)
#             print(f"\n✓ Success for {num}:")
#             print(f"  Country: {result['country_name']}")
#             print(f"  Carrier: {result['carrier']}")
#             print(f"  International: {result['formatted_international']}")
#         except ValueError as e:
#             print(f"\n✗ Error for {num}: {e}")