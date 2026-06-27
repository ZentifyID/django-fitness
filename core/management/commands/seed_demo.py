"""
Заполнение базы демонстрационными данными.

Использование:
    python manage.py seed_demo            # добавить демо-данные (идемпотентно)
    python manage.py seed_demo --flush    # сначала очистить старые демо-данные

Команда переиспользует картинки, которые уже лежат в папке media/
(media/blog/*, media/trainers/*) — отдельно загружать ничего не нужно.
"""

import os
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from blog.models import Post
from members.models import MembershipPlan, MemberProfile
from schedule.models import Trainer, Activity, Schedule, Booking, TrainerReview

DEMO_PASSWORD = "demo12345"

# Картинки, которые уже есть в media/. Путь — относительно MEDIA_ROOT,
# именно его и хранит ImageField.
TRAINER_PHOTOS = [
    "trainers/expressive-redhead-guy-beige-shirt_176420-32329.avif",
    "trainers/handsome-young-cheerful-man-with-arms-crossed_171337-1073.avif",
    "trainers/young-confident-woman-with-blond-curly-hair-cross-arms-chest-look-54132.avif",
]
BLOG_IMAGES = ["blog/eda.jpg", "blog/sport.jpg"]


class Command(BaseCommand):
    help = "Заполняет базу демонстрационными данными (с картинками из media/)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Удалить ранее созданные демо-данные перед заполнением.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        from django.conf import settings

        self.media_root = settings.MEDIA_ROOT

        if options["flush"]:
            self._flush()

        admin = self._create_users()
        plans = self._create_plans()
        self._assign_memberships(plans)
        trainers = self._create_trainers()
        activities = self._create_activities()
        self._create_schedule(activities, trainers)
        self._create_bookings()
        self._create_reviews(trainers)
        self._create_blog(admin, trainers)

        self.stdout.write(self.style.SUCCESS("\nГотово! Демо-данные загружены."))
        self.stdout.write("Учётные записи для входа:")
        self.stdout.write("  admin / admin12345   (суперпользователь, /admin/)")
        self.stdout.write(f"  demo_anna, demo_ivan, demo_oleg, demo_maria / {DEMO_PASSWORD}")

    # ------------------------------------------------------------------ #
    def _img(self, relpath):
        """Вернуть путь к картинке, если файл реально существует в media/."""
        full = os.path.join(self.media_root, relpath.replace("/", os.sep))
        if os.path.exists(full):
            return relpath
        self.stdout.write(self.style.WARNING(f"  ! картинка не найдена: {relpath}"))
        return None

    def _flush(self):
        self.stdout.write("Очистка старых демо-данных...")
        Booking.objects.all().delete()
        TrainerReview.objects.all().delete()
        Schedule.objects.all().delete()
        Activity.objects.all().delete()
        Trainer.objects.all().delete()
        Post.objects.all().delete()
        MemberProfile.objects.all().delete()
        MembershipPlan.objects.all().delete()
        User.objects.filter(username__startswith="demo_").delete()

    def _create_users(self):
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password("admin12345")
            admin.save()

        demo_users = [
            ("demo_anna", "Анна", "Смирнова"),
            ("demo_ivan", "Иван", "Петров"),
            ("demo_oleg", "Олег", "Кузнецов"),
            ("demo_maria", "Мария", "Иванова"),
        ]
        for username, first, last in demo_users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first, "last_name": last, "email": f"{username}@example.com"},
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
        self.stdout.write(self.style.SUCCESS("Пользователи созданы."))
        return admin

    def _create_plans(self):
        data = [
            ("Разовое посещение", "Один визит в зал без обязательств.", Decimal("500.00"), 1),
            ("Месячный", "Безлимитное посещение в течение месяца.", Decimal("3000.00"), 30),
            ("Полугодовой", "Выгодный абонемент на 6 месяцев.", Decimal("15000.00"), 180),
            ("Годовой", "Максимальная выгода — год тренировок.", Decimal("25000.00"), 365),
        ]
        plans = {}
        for name, desc, price, days in data:
            plan, _ = MembershipPlan.objects.get_or_create(
                name=name,
                defaults={"description": desc, "price": price, "duration_days": days},
            )
            plans[name] = plan
        self.stdout.write(self.style.SUCCESS("Тарифные планы созданы."))
        return plans

    def _assign_memberships(self, plans):
        today = timezone.now().date()
        mapping = [
            ("demo_anna", "Годовой", "+79001112233", 300, False),
            ("demo_ivan", "Месячный", "+79002223344", 12, False),
            ("demo_oleg", "Полугодовой", "+79003334455", 90, True),
            ("demo_maria", "Месячный", "+79004445566", 3, False),
        ]
        for username, plan_name, phone, days_left, frozen in mapping:
            user = User.objects.get(username=username)
            MemberProfile.objects.update_or_create(
                user=user,
                defaults={
                    "phone": phone,
                    "membership": plans[plan_name],
                    "membership_expires": today + timedelta(days=days_left),
                    "is_frozen": frozen,
                    "freeze_start": today if frozen else None,
                },
            )
        self.stdout.write(self.style.SUCCESS("Профили клиентов и абонементы назначены."))

    def _create_trainers(self):
        data = [
            ("Дмитрий Соколов", "Силовые тренировки, кроссфит",
             "Мастер спорта по тяжёлой атлетике, 8 лет опыта персональных тренировок."),
            ("Артём Волков", "Бокс, функциональный тренинг",
             "Кандидат в мастера спорта по боксу. Поможет привести тело в тонус."),
            ("Екатерина Лебедева", "Йога, пилатес, стретчинг",
             "Сертифицированный инструктор по йоге. Работает с гибкостью и осанкой."),
        ]
        trainers = []
        for i, (name, spec, bio) in enumerate(data):
            trainer, _ = Trainer.objects.get_or_create(
                name=name,
                defaults={"specialization": spec, "bio": bio},
            )
            photo = self._img(TRAINER_PHOTOS[i % len(TRAINER_PHOTOS)])
            if photo and not trainer.photo:
                trainer.photo.name = photo
                trainer.save(update_fields=["photo"])
            trainers.append(trainer)
        self.stdout.write(self.style.SUCCESS("Тренеры созданы (с фото)."))
        return trainers

    def _create_activities(self):
        data = [
            ("Силовая тренировка", "Работа со свободными весами и тренажёрами.", 60, "#E53935"),
            ("Кроссфит", "Высокоинтенсивная функциональная тренировка.", 50, "#FB8C00"),
            ("Йога", "Спокойная практика на гибкость и расслабление.", 75, "#43A047"),
            ("Бокс", "Постановка удара, работа на мешках.", 60, "#3949AB"),
            ("Пилатес", "Укрепление мышц кора и улучшение осанки.", 55, "#8E24AA"),
            ("Сайкл", "Кардио на велотренажёрах под музыку.", 45, "#00ACC1"),
        ]
        activities = []
        for name, desc, dur, color in data:
            act, _ = Activity.objects.get_or_create(
                name=name,
                defaults={"description": desc, "duration_minutes": dur, "color": color},
            )
            activities.append(act)
        self.stdout.write(self.style.SUCCESS("Виды занятий созданы."))
        return activities

    def _create_schedule(self, activities, trainers):
        now = timezone.now()
        # Старт сегодня в 8:00 по локальному времени.
        base = now.replace(hour=8, minute=0, second=0, microsecond=0)
        created = 0
        # На 7 дней вперёд, по 3 занятия в день (10:00, 14:00, 18:00).
        for day in range(7):
            for slot, hour in enumerate((10, 14, 18)):
                start = base + timedelta(days=day)
                start = start.replace(hour=hour)
                if start < now:
                    continue
                activity = activities[(day * 3 + slot) % len(activities)]
                trainer = trainers[(day + slot) % len(trainers)]
                _, was_created = Schedule.objects.get_or_create(
                    activity=activity,
                    start_time=start,
                    defaults={"trainer": trainer, "capacity": 10 + (slot * 2)},
                )
                created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Расписание создано (новых записей: {created})."))

    def _create_bookings(self):
        usernames = ["demo_anna", "demo_ivan", "demo_oleg", "demo_maria"]
        users = list(User.objects.filter(username__in=usernames))
        upcoming = list(Schedule.objects.order_by("start_time")[:6])
        count = 0
        for i, sched in enumerate(upcoming):
            # Записываем по 2 клиента на занятие.
            for user in (users[i % len(users)], users[(i + 1) % len(users)]):
                _, created = Booking.objects.get_or_create(schedule=sched, user=user)
                count += int(created)
        self.stdout.write(self.style.SUCCESS(f"Брони на занятия созданы (новых: {count})."))

    def _create_reviews(self, trainers):
        users = list(User.objects.filter(username__startswith="demo_"))
        review_texts = [
            (5, "Отличный тренер, всё доступно объясняет!"),
            (4, "Хорошие тренировки, результат заметен."),
            (5, "Очень довольна занятиями, рекомендую."),
        ]
        count = 0
        for t_idx, trainer in enumerate(trainers):
            for r_idx in range(2):
                user = users[(t_idx + r_idx) % len(users)]
                rating, text = review_texts[(t_idx + r_idx) % len(review_texts)]
                _, created = TrainerReview.objects.get_or_create(
                    trainer=trainer,
                    user=user,
                    defaults={"rating": rating, "text": text},
                )
                count += int(created)
        self.stdout.write(self.style.SUCCESS(f"Отзывы о тренерах созданы (новых: {count})."))

    def _create_blog(self, admin, trainers):
        posts = [
            ("Правильное питание для набора массы",
             "Чтобы набирать качественную мышечную массу, важно соблюдать профицит "
             "калорий и следить за балансом белков, жиров и углеводов. В этой статье "
             "разбираем базовые принципы спортивного питания и примерное меню на день.",
             BLOG_IMAGES[0]),
            ("5 упражнений для начинающих",
             "Если вы только пришли в зал, не нужно сразу гнаться за большими весами. "
             "Начните с базовых движений: приседания, жим, тяга, планка и выпады. "
             "Правильная техника на старте — залог прогресса без травм.",
             BLOG_IMAGES[1]),
        ]
        count = 0
        for title, content, image_rel in posts:
            post, created = Post.objects.get_or_create(
                title=title,
                defaults={"content": content, "author": admin},
            )
            image = self._img(image_rel)
            if image and not post.image:
                post.image.name = image
                post.save(update_fields=["image"])
            count += int(created)
        self.stdout.write(self.style.SUCCESS(f"Статьи блога созданы (новых: {count})."))
