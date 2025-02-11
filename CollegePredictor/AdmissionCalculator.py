
from typing import Dict, List
from datetime import datetime
import numpy as np

class AdmissionsCalculator:
    def __init__(self, institution_weights: Dict, mission_metrics: Dict, school_profiles: Dict):
        self.weights = institution_weights
        self.mission_metrics = mission_metrics
        self.school_profiles = school_profiles
        self.audit_log = []
        self.historical_data = []
        
        # Initialize default thresholds
        self.thresholds = {'Safety': 0.7, 'Target': 0.5, 'Reach': 0.3}

    class Student:
        def __init__(self, academic_data: Dict, context_data: Dict, 
                    contributions: Dict, mission_alignment: Dict):
            self.academic = academic_data
            self.context = context_data
            self.contributions = contributions
            self.mission_alignment = mission_alignment

    def log_audit(self, action: str, metadata: Dict):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'metadata': metadata
        }
        self.audit_log.append(entry)

    def normalize_gpa(self, student: Student) -> float:
        # Get school context for GPA normalization
        school_profile = self.school_profiles.get(student.context['school_id'], {})
        if not school_profile:
            self.log_audit('missing_school_profile', {'school': student.context['school_id']})
            return student.academic['gpa'] / 4.0  # Simple normalization fallback

        school_mean = school_profile.get('gpa_mean', 3.0)
        school_std = school_profile.get('gpa_std', 0.5)
        z_score = (student.academic['gpa'] - school_mean) / school_std
        return 1 / (1 + np.exp(-z_score))  # Sigmoid normalization

    def calculate_academic_score(self, student: Student) -> float:
        gpa_score = self.normalize_gpa(student)
        test_score = student.academic['test_scores'] / 1600  # SAT normalization
        
        # Dynamic weighting based on school competitiveness
        school_competitiveness = self.school_profiles.get(
            student.context['school_id'], {}).get('competitiveness', 1.0)
        academic_score = (gpa_score * 0.6 + test_score * 0.4) * school_competitiveness
        
        self.log_audit('academic_score_calculated', {
            'gpa_score': gpa_score,
            'test_score': test_score,
            'final_score': academic_score
        })
        return min(academic_score, 1.0)  # Cap at 1.0

    def calculate_mission_fit(self, student: Student) -> float:
        fit_score = sum(
            student.mission_alignment.get(metric, 0) * weight 
            for metric, weight in self.mission_metrics.items()
        )
        return fit_score / sum(self.mission_metrics.values())  # Normalize

    def apply_context_modifiers(self, student: Student, base_score: float) -> float:
        adjustments = 0
        # Socioeconomic adjustment
        if student.context.get('low_income', False):
            adjustments += 0.05
        # Adversity adjustment
        adjustments += student.context.get('adversity_score', 0) * 0.1
        # Legal compliance check
        if self.check_legal_compliance(student):
            adjustments += student.context.get('underrepresented_group', 0) * 0.03
        
        self.log_audit('context_adjustments_applied', {
            'base_score': base_score,
            'adjustments': adjustments
        })
        return min(base_score + adjustments, 1.0)

    def check_legal_compliance(self, student: Student) -> bool:
        # Placeholder for actual legal checks
        # Would include race/ethnicity usage compliance
        return True

    def calculate_confidence_score(self, student: Student) -> float:
        # Placeholder for actual confidence calculation
        # Would use historical data and prediction variance
        return 0.8  # Temporary fixed value

    def analyze_intersectionality(self, student: Student) -> float:
        # Placeholder for AI/human rubric analysis
        # Example simple implementation:
        intersection_score = 0
        if student.context.get('adversity_score', 0) > 0.7 and \
           student.contributions.get('leadership', 0) > 0.5:
            intersection_score += 0.05
        return intersection_score

    def calculate_total_score(self, student: Student) -> Dict:
        academic = self.calculate_academic_score(student)
        contributions = student.contributions['total']
        mission_fit = self.calculate_mission_fit(student)
        
        base_score = (
            academic * self.weights['academic'] +
            contributions * self.weights['contributions'] +
            mission_fit * self.weights['mission_fit']
        )
        
        context_adjusted = self.apply_context_modifiers(student, base_score)
        intersection_bonus = self.analyze_intersectionality(student)
        confidence = self.calculate_confidence_score(student)
        
        final_score = min(context_adjusted + intersection_bonus, 1.0)
        
        return {
            'final_score': final_score,
            'confidence': confidence,
            'category': self.classify_application(final_score, confidence),
            'component_scores': {
                'academic': academic,
                'contributions': contributions,
                'mission_fit': mission_fit
            }
        }

    def classify_application(self, score: float, confidence: float) -> str:
        if score >= self.thresholds['Safety'] and confidence >= 0.7:
            return 'Safety'
        elif score >= self.thresholds['Target'] and confidence >= 0.5:
            return 'Target'
        elif score >= self.thresholds['Reach']:
            return 'Reach'
        return 'Below Threshold'

    def update_weights(self, new_weights: Dict):
        self.weights = new_weights
        self.log_audit('weights_updated', {'new_weights': new_weights})

    def add_historical_data(self, student_data: Dict, admission_outcome: bool):
        self.historical_data.append({
            'student': student_data,
            'outcome': admission_outcome,
            'timestamp': datetime.now().isoformat()
        })

# Example Usage
if __name__ == "__main__":
    # Institution configuration
    config = {
        'weights': {
            'academic': 0.4,
            'contributions': 0.3,
            'mission_fit': 0.3
        },
        'mission_metrics': {
            'diversity': 0.4,
            'community_impact': 0.6
        },
        'school_profiles': {
            'HS_123': {  # Competitive school
                'gpa_mean': 3.8,
                'gpa_std': 0.2,
                'competitiveness': 1.2
            },
            'HS_456': {  # Less competitive school
                'gpa_mean': 3.4,
                'gpa_std': 0.4,
                'competitiveness': 0.9
            }
        }
    }

    # Initialize calculator
    calculator = AdmissionsCalculator(
        config['weights'],
        config['mission_metrics'],
        config['school_profiles']
    )

    # Create a sample student
    student_data = {
        'academic': {'gpa': 3.7, 'test_scores': 1450},
        'context': {
            'school_id': 'HS_123',
            'low_income': True,
            'adversity_score': 0.8
        },
        'contributions': {'total': 0.85, 'leadership': 0.9},
        'mission_alignment': {'diversity': 0.7, 'community_impact': 0.8}
    }
    
    #student = calculator.Student(**student_data)
    student = calculator.Student(
    student_data['academic'],
    student_data['context'],
    student_data['contributions'],
    student_data['mission_alignment']
    )
    
    # Calculate scores
    result = calculator.calculate_total_score(student)
    print("Admissions Result:")
    print(f"Final Score: {result['final_score']:.2f}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Category: {result['category']}")
    print("Component Scores:")
    for k, v in result['component_scores'].items():
        print(f"  {k}: {v:.2f}")
