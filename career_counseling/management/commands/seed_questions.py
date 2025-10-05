from django.core.management.base import BaseCommand
from career_counseling.models import Question

class Command(BaseCommand):
    help = 'Seeds the database with assessment questions'

    def handle(self, *args, **kwargs):
        questions = [
            {
                'text': 'When faced with a complex problem, how do you prefer to approach it?',
                'options': [
                    'Break it down into smaller parts and solve systematically',
                    'Brainstorm multiple solutions and choose the best one',
                    'Research similar problems and adapt existing solutions',
                    'Collaborate with others to find innovative solutions'
                ],
                'categories': ['problem_solving', 'work_style']
            },
            {
                'text': 'In a team project, what role do you naturally take?',
                'options': [
                    'Leader who coordinates and makes decisions',
                    'Creative thinker who generates ideas',
                    'Detail-oriented executor who ensures quality',
                    'Mediator who helps resolve conflicts'
                ],
                'categories': ['leadership', 'teamwork']
            },
            {
                'text': 'How do you prefer to learn new skills?',
                'options': [
                    'Hands-on practice and experimentation',
                    'Reading documentation and following tutorials',
                    'Taking structured courses with clear objectives',
                    'Learning from others through observation and discussion'
                ],
                'categories': ['learning_style']
            },
            {
                'text': 'When working on a project, what motivates you the most?',
                'options': [
                    'Solving challenging technical problems',
                    'Creating something visually appealing',
                    'Helping others and making a positive impact',
                    'Achieving measurable results and success'
                ],
                'categories': ['motivation']
            },
            {
                'text': 'How do you handle tight deadlines?',
                'options': [
                    'Plan ahead and work systematically',
                    'Work best under pressure and thrive in fast-paced environments',
                    'Break tasks into manageable chunks and track progress',
                    'Collaborate with others to meet deadlines efficiently'
                ],
                'categories': ['work_style', 'stress_management']
            },
            {
                'text': 'What type of work environment do you prefer?',
                'options': [
                    'Structured and organized with clear procedures',
                    'Dynamic and flexible with room for creativity',
                    'Fast-paced and challenging with constant learning',
                    'Collaborative and social with frequent interaction'
                ],
                'categories': ['work_environment']
            },
            {
                'text': 'How do you prefer to communicate complex ideas?',
                'options': [
                    'Using data and visualizations',
                    'Through storytelling and examples',
                    'Written documentation and reports',
                    'Interactive discussions and presentations'
                ],
                'categories': ['communication_style']
            },
            {
                'text': 'What aspect of technology interests you the most?',
                'options': [
                    'Building and developing new systems',
                    'Designing user interfaces and experiences',
                    'Analyzing and interpreting data',
                    'Managing and optimizing processes'
                ],
                'categories': ['technical_interests']
            },
            {
                'text': 'How do you approach decision-making?',
                'options': [
                    'Rely on data and logical analysis',
                    'Consider multiple perspectives and possibilities',
                    'Trust intuition and experience',
                    'Seek consensus and collaboration'
                ],
                'categories': ['decision_making']
            },
            {
                'text': 'What type of impact do you want to make in your career?',
                'options': [
                    'Innovating and creating new solutions',
                    'Improving existing systems and processes',
                    'Helping others achieve their goals',
                    'Contributing to organizational success'
                ],
                'categories': ['career_goals']
            }
        ]

        for q_data in questions:
            question = Question.objects.create(
                text=q_data['text'],
                options=q_data['options'],
                categories=q_data['categories']
            )
            self.stdout.write(f'Created question: {question.text}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded questions')) 