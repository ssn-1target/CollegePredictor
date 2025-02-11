import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class SchoolProfile:
    id: str
    name: str
    gpa_mean: Optional[float] = None
    gpa_std: Optional[float] = None
    competitiveness: Optional[float] = None
    ap_courses: Optional[int] = None
    data_source: str = "unknown"

class SchoolProfileBuilder:
    def __init__(self):
        self.cache = {}  # Simple in-memory cache
        
    def get_school_profile(self, school_id: str) -> SchoolProfile:
        # Check cache first
        if school_id in self.cache:
            return self.cache[school_id]
        
        # Try data sources in priority order
        profile = self._get_nces_data(school_id) or \
                  self._get_cde_data(school_id) or \
                  self._scrape_school_data(school_id)
        
        # Validate minimum data requirements
        if profile.gpa_mean is None:
            profile = self._estimate_gpa_stats(profile)
            
        self.cache[school_id] = profile
        return profile
    
    def _get_nces_data(self, school_id: str) -> Optional[SchoolProfile]:
        """National Center for Education Statistics API"""
        try:
            # Mock NCES API response
            nces_data = {
                "school_name": "Sample High School",
                "gpa_mean": 3.4,
                "gpa_std": 0.3,
                "ap_courses": 15
            }
            
            return SchoolProfile(
                id=school_id,
                name=nces_data["school_name"],
                gpa_mean=nces_data["gpa_mean"],
                gpa_std=nces_data["gpa_std"],
                ap_courses=nces_data["ap_courses"],
                data_source="nces"
            )
        except Exception as e:
            print(f"NCES API Error: {str(e)}")
            return None

    def _get_cde_data(self, school_id: str) -> Optional[SchoolProfile]:
        """California Department of Education Data"""
        try:
            # Mock CDE API response
            cde_data = {
                "school_name": "CA Sample High",
                "uc_csu_eligibility": 0.72,
                "ap_count": 22
            }
            
            # Convert UC eligibility rate to estimated GPA
            return SchoolProfile(
                id=school_id,
                name=cde_data["school_name"],
                gpa_mean=self._uc_eligibility_to_gpa(cde_data["uc_csu_eligibility"]),
                gpa_std=0.25,  # Default assumption
                ap_courses=cde_data["ap_count"],
                data_source="cde"
            )
        except Exception as e:
            print(f"CDE API Error: {str(e)}")
            return None
    
    def _scrape_school_data(self, school_id: str) -> SchoolProfile:
        """Fallback web scraper"""
        try:
            # Mock school website URL pattern
            url = f"https://www.{school_id}.edu/profile"
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Example scraping logic
            name = soup.find('h1', class_='school-name').text
            gpa_text = soup.find('div', class_='stats').text
            gpa_mean = float(gpa_text.split("Average GPA: ")[1].split()[0])
            
            return SchoolProfile(
                id=school_id,
                name=name,
                gpa_mean=gpa_mean,
                gpa_std=0.3,  # Default assumption
                data_source="web_scraping"
            )
        except Exception as e:
            print(f"Scraping Error: {str(e)}")
            return SchoolProfile(id=school_id, name="Unknown School")
    
    def _uc_eligibility_to_gpa(self, eligibility_rate: float) -> float:
        """Convert UC eligibility rate to estimated GPA (California-specific)"""
        # Based on historical correlation
        return round(3.0 + (eligibility_rate * 0.7), 1)
    
    def _estimate_gpa_stats(self, profile: SchoolProfile) -> SchoolProfile:
        """Fallback estimation when no data available"""
        if profile.ap_courses:
            profile.gpa_mean = 3.2 + (profile.ap_courses * 0.02)
            profile.gpa_std = 0.35
        else:
            profile.gpa_mean = 3.0
            profile.gpa_std = 0.4
        return profile

# Usage Example
if __name__ == "__main__":
    builder = SchoolProfileBuilder()
    
    # Try with official data first
    school = builder.get_school_profile("nces_12345")
    print(f"Official Data Profile:\n{school}\n")
    
    # Force fallback to scraping
    unknown_school = builder.get_school_profile("unknown_HS_456")
    print(f"Scraped Profile:\n{unknown_school}")   