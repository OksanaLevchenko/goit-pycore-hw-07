from collections import UserDict
from datetime import datetime, date, timedelta


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Not enough arguments."
    return wrapper


class Field:
    def __init__(self, value):
        self.value = value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        value = str(value)
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone must have 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            dt = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(dt.date())


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone = str(phone)
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError("Phone not found.")

    def edit_phone(self, old_phone, new_phone):
        old_phone = str(old_phone)
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Old phone not found.")

    def find_phone(self, phone):
        phone = str(phone)
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = ", ".join(p.value for p in self.phones) if self.phones else "-"
        bday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "-"
        return f"{self.name.value}: {phones} | birthday: {bday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name not in self.data:
            raise KeyError
        del self.data[name]

    def get_upcoming_birthdays(self):
        today = date.today()
        end_day = today + timedelta(days=7)
        result = []

        for name, record in self.data.items():
            if record.birthday is None:
                continue

            bday = record.birthday.value
            next_bday = bday.replace(year=today.year)
            if next_bday < today:
                next_bday = next_bday.replace(year=today.year + 1)

            if today <= next_bday <= end_day:
                congrats_day = next_bday
                if congrats_day.weekday() == 5:
                    congrats_day = congrats_day + timedelta(days=2)
                elif congrats_day.weekday() == 6:
                    congrats_day = congrats_day + timedelta(days=1)

                result.append(
                    {"name": name, "congratulation_date": congrats_day.strftime("%d.%m.%Y")}
                )

        result.sort(key=lambda x: datetime.strptime(x["congratulation_date"], "%d.%m.%Y").date())
        return result


def parse_input(user_input):
    user_input = user_input.strip()
    if not user_input:
        return "", []
    parts = user_input.split()
    command = parts[0].lower()
    args = parts[1:]
    return command, args


@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return "Phone changed."


@input_error
def show_phone(args, book):
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    if not record.phones:
        return "No phones."
    return ", ".join(p.value for p in record.phones)


@input_error
def show_all(book):
    if not book.data:
        return "No contacts."
    lines = []
    for record in book.data.values():
        lines.append(str(record))
    return "\n".join(lines)


@input_error
def add_birthday(args, book):
    name, bday, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    record.add_birthday(bday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    if record.birthday is None:
        return "Birthday not set."
    return record.birthday.value.strftime("%d.%m.%Y")


@input_error
def birthdays(args, book):
    items = book.get_upcoming_birthdays()
    if not items:
        return "No birthdays in the next 7 days."
    lines = []
    for it in items:
        lines.append(f"{it['name']}: {it['congratulation_date']}")
    return "\n".join(lines)


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()