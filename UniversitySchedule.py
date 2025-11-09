import pandas as pd
import random
from collections import defaultdict


class UniversityScheduleGenerator:
    def __init__(self):
        self.teachers = []
        self.groups = []
        self.classrooms = []
        self.lessons = []
        self.schedule = defaultdict(lambda: defaultdict(list))
        self.days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
        self.time_slots = ['09:00-10:35', '10:45-12:20', '13:20-14:55', '15:05-16:40', '16:50-18:25']
        self.stats = {'total_lessons': 0, 'scheduled': 0, 'conflicts': 0}

    def load_teachers_from_csv(self, filename='преподаватели_и_предметы.csv'):
        try:
            data = pd.read_csv(filename, encoding='utf-8-sig')
            self.teachers = [{
                'id': idx + 1,
                'name': row['Преподаватель'],
                'subjects': [s.strip() for s in str(row['Предметы']).split(',')],
                'department': row.get('Кафедра', 'Общая'),
                'max_lessons_per_day': random.randint(3, 5),
                'preferred_times': random.sample(self.time_slots, 3)
            } for idx, row in data.iterrows()]
            print(f"Загружено преподавателей: {len(self.teachers)}")
            return True
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return False

    def generate_groups(self):
        group_names = [
            'ИВТ-11БО', 'ИВТ-12БО', 'ИВТ-13БО', 'ИТ-11БО', 'ИТ-12БО',
            'ПИЭ-11БО', 'ПИЭ-12БО', 'ПИЭ-14БО', 'ИВТ-21БО', 'ИВТ-22БО',
            'ИТ-21БО', 'ИТ-22БО', 'ПИЭ-21БО', 'ПИЭ-22БО', 'ИВТ-31БО',
            'ИВТ-32БО', 'ИТ-31БО', 'ИТ-32БО', 'ПИЭ-31БО', 'ПИЭ-32БО',
            'ИВТ-41БО', 'ИВТ-42БО', 'ИТ-41БО', 'ИТ-42БО', 'ПИЭ-41БО'
        ]
        self.groups = [{
            'id': idx + 1,
            'name': name,
            'lessons_per_week': random.randint(20, 30),
            'max_lessons_per_day': random.randint(3, 5)
        } for idx, name in enumerate(group_names)]

    def generate_classrooms(self):
        classroom_data = [
            {'name': 'ауд. 201', 'type': 'Компьютерный'},
            {'name': 'ауд. 210', 'type': 'Компьютерный'},
            {'name': 'ауд. 213', 'type': 'Компьютерный'},
            {'name': 'ауд. 216', 'type': 'Компьютерный'},
            {'name': 'ауд. 221', 'type': 'Компьютерный'},
            {'name': 'ауд. 203', 'type': 'Лекционная'},
            {'name': 'ауд. 204', 'type': 'Лекционная'},
            {'name': 'ауд. 207', 'type': 'Лекционная'},
            {'name': 'ауд. 215', 'type': 'Лекционная'},
            {'name': 'ауд. 219', 'type': 'Лекционная'},
            {'name': 'ауд. 220', 'type': 'Лекционная'},
            {'name': 'ауд. 224', 'type': 'Лекционная'},
            {'name': 'ауд. 226', 'type': 'Лекционная'},
            {'name': 'ауд. 301', 'type': 'Лекционная'},
            {'name': 'ауд. 304', 'type': 'Лекционная'},
            {'name': 'ауд. 309', 'type': 'Лекционная'},
            {'name': 'ауд. 312', 'type': 'Лекционная'},
            {'name': 'ауд. 208', 'type': 'Языковая'},
            {'name': 'ауд. 305', 'type': 'Языковая'},
            {'name': 'ауд. 306', 'type': 'Языковая'}
        ]
        self.classrooms = [{'id': idx + 1, **room} for idx, room in enumerate(classroom_data)]

    def determine_classroom_type(self, subject_name):
        lower_name = subject_name.lower()
        if any(word in lower_name for word in ['программирование', 'информатик', 'компьютер', 'алгоритм']):
            return 'Компьютерный'
        if any(word in lower_name for word in ['иностранный', 'язык']):
            return 'Языковая'
        return 'Лекционная'

    def create_lessons_list(self):
        lesson_id = 1
        for group in self.groups:
            scheduled_lessons = 0
            subject_teacher_pairs = [(subject, teacher) for teacher in self.teachers for subject in teacher['subjects']]
            random.shuffle(subject_teacher_pairs)
            for subject, teacher in subject_teacher_pairs:
                if scheduled_lessons >= group['lessons_per_week']:
                    break
                hours = random.randint(1, 2)
                hours = min(hours, group['lessons_per_week'] - scheduled_lessons)
                for _ in range(hours):
                    self.lessons.append({
                        'id': lesson_id,
                        'group': group['name'],
                        'group_id': group['id'],
                        'subject': subject,
                        'teacher': teacher['name'],
                        'teacher_id': teacher['id'],
                        'classroom_type': self.determine_classroom_type(subject),
                        'priority': random.randint(1, 3)
                    })
                    lesson_id += 1
                    scheduled_lessons += 1
        self.stats['total_lessons'] = len(self.lessons)

    def has_conflict(self, day, time_slot, lesson, classroom, schedule):
        for existing in schedule[day][time_slot]:
            if existing['teacher'] == lesson['teacher']:
                return True
            if existing['group'] == lesson['group']:
                return True
            if existing['classroom'] == classroom['name']:
                return True
        if classroom['type'] != lesson['classroom_type']:
            return True

        teacher_load_today = sum(1 for lessons in schedule[day].values() for l in lessons if l['teacher'] == lesson['teacher'])
        group_load_today = sum(1 for lessons in schedule[day].values() for l in lessons if l['group'] == lesson['group'])

        teacher_max = next(t['max_lessons_per_day'] for t in self.teachers if t['id'] == lesson['teacher_id'])
        group_max = next(g['max_lessons_per_day'] for g in self.groups if g['name'] == lesson['group'])

        return teacher_load_today >= teacher_max or group_load_today >= group_max

    def generate_schedule(self, attempts=30):
        best_schedule = None
        max_scheduled_lessons = 0

        for attempt in range(attempts):
            temp_schedule = defaultdict(lambda: defaultdict(list))
            lessons_to_schedule = self.lessons.copy()
            random.shuffle(lessons_to_schedule)
            scheduled_count = 0

            for lesson in lessons_to_schedule:
                scheduled = False
                for day in random.sample(self.days, len(self.days)):
                    for time_slot in random.sample(self.time_slots, len(self.time_slots)):
                        available_classroom = next(
                            (room for room in self.classrooms
                             if room['type'] == lesson['classroom_type']
                             and not self.has_conflict(day, time_slot, lesson, room, temp_schedule)),
                            None
                        )
                        if available_classroom:
                            temp_schedule[day][time_slot].append({**lesson, 'day': day, 'time': time_slot, 'classroom': available_classroom['name']})
                            scheduled_count += 1
                            scheduled = True
                            break
                    if scheduled:
                        break

            if scheduled_count > max_scheduled_lessons:
                max_scheduled_lessons = scheduled_count
                best_schedule = temp_schedule

        self.schedule = best_schedule or defaultdict(lambda: defaultdict(list))
        self.stats['scheduled'] = max_scheduled_lessons
        print(f"Лучший результат: {max_scheduled_lessons}/{self.stats['total_lessons']} уроков размещено из {attempts} попыток")

    def save_schedule_to_csv(self, filename='университетское_расписание.csv'):
        rows = [{
            'День': day,
            'Время': time_slot,
            'Группа': lesson['group'],
            'Предмет': lesson['subject'],
            'Преподаватель': lesson['teacher'],
            'Аудитория': lesson['classroom'],
            'Тип аудитории': lesson['classroom_type']
        } for day in self.days for time_slot in self.time_slots for lesson in self.schedule[day][time_slot]]
        pd.DataFrame(rows).to_csv(filename, index=False, encoding='utf-8-sig')


def main():
    generator = UniversityScheduleGenerator()
    if not generator.load_teachers_from_csv():
        print("Ошибка: данные не загружены.")
        return
    generator.generate_groups()
    generator.generate_classrooms()
    generator.create_lessons_list()
    generator.generate_schedule()
    generator.save_schedule_to_csv()


if __name__ == "__main__":
    main()
