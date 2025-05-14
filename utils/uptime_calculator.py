from datetime import date
from dateutil.relativedelta import relativedelta
from utils.config import setup_logger

logger = setup_logger("UptimeCalculator")

def validate_date(start_date: date) -> bool:
    """Validate that the start date is not in the future and is reasonable."""
    if not isinstance(start_date, date):
        logger.error("Invalid date type provided")
        return False
    
    current_date = date.today()
    if start_date > current_date:
        logger.error("Start date cannot be in the future")
        return False
    
    # Assuming people don't live more than 150 years
    max_age = date(1900, 1, 1)
    if start_date < max_age:
        logger.error("Start date is unreasonably old")
        return False
    
    return True

def calculate_uptime(start_date: date, expectancy_days: int = 26783) -> dict:
    """
    Calculate uptime statistics based on a start date.
    
    Args:
        start_date: The starting date (e.g., birth date)
        expectancy_days: Expected lifespan in days (default ~73.5 years)
    
    Returns:
        Dictionary containing uptime statistics
    """
    default_stats = {
        'years': 0,
        'months': 0,
        'days': 0,
        'total_days': 0,
        'life_percentage': 0.0,
        'years_rounded': 0.0
    }
    
    try:
        if not validate_date(start_date):
            return default_stats
            
        if expectancy_days <= 0:
            logger.error("Life expectancy must be positive")
            return default_stats
            
        current_date = date.today()
        difference = relativedelta(current_date, start_date)
        total_days = (current_date - start_date).days
        life_percentage = round((total_days / expectancy_days) * 100, 2)
        years_rounded = round(total_days / 365.25, 2)  # Using 365.25 to account for leap years
        
        stats = {
            'years': difference.years,
            'months': difference.months,
            'days': difference.days,
            'total_days': total_days,
            'life_percentage': life_percentage,
            'years_rounded': years_rounded
        }
        
        logger.info(f"Uptime calculated successfully for start date {start_date} "
                   f"(total_days={total_days}, life_percentage={life_percentage}%)")
        return stats
        
    except Exception as e:
        logger.error(f"Error calculating uptime: {str(e)}")
        return default_stats
