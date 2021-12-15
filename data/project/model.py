from __future__ import annotations

from dataclasses import field, dataclass
import random
from typing import Type, cast

from faker import Faker
import faker.providers.job
import faker.providers.address
import faker.providers.person
from data.project.base import Dataset, Entity

fake = Faker()

@dataclass
class RentalDataset(Dataset):
    people: list[Person]
    addresses: list[Address]
    jobs: list[Job]
    transactions: list[Transaction]

    @staticmethod
    def entity_types() -> list[Type[Entity]]:
        return [Person, Address, Job, Transaction]

    @staticmethod
    def from_sequence(entities: list[list[Entity]]) -> Dataset:
        return RentalDataset(
            cast(list[Person], entities[0]),
            cast(list[Address], entities[1]),
            cast(list[Job], entities[2]),
            cast(list[Transaction], entities[3])
        )

    def entities(self) -> dict[Type[Entity], list[Entity]]:
        res = dict()
        res[Person] = self.people
        res[Address] = self.addresses
        res[Job] = self.jobs
        res[Transaction] = self.transactions

        return res

    @staticmethod
    def generate(
        count_of_customers: int,
        count_of_addresses: int,
        count_of_jobs: int,
        count_of_transactions: int):


        def generate_people(n: int, male_ratio: float = 0.5, locale: str = "en_US",
                            unique: bool = False, min_age: int = 15, max_age: int = 100) -> list[Person]:
            assert n > 0
            assert 0 <= male_ratio <= 1
            assert 0 <= min_age <= max_age

            fake = Faker(locale)
            people = []
            for i in range(n):
                male = random.random() < male_ratio
                generator = fake if not unique else fake.unique
                people.append(Person(
                    "P-" + (str(i).zfill(6)),
                    generator.name_male() if male else generator.name_female(),
                    random.randint(min_age, max_age),
                    male))

            return people

        def generate_address(n: int) -> list[Address]:
            assert n > 0

            addresses = []
            for i in range(n):
                try:
                    address = Address(
                        fake.postcode(),
                        fake.country(),
                        fake.city(),
                        fake.street_name(),
                    )
                    addresses.append(address)
                except:
                    break
            return addresses

        def generate_job(n: int) -> list[Job]:
            assert n > 0

            jobs = []
            for i in range(n):
                try:
                    x = Job(
                        fake.job
                    )
                    jobs.append(x)

                except:
                    break
            return jobs

        def generate_transactions(n: int, people: list[Person], cars: list[Address], airports: list[Job]) -> list[
            Transaction]:
            assert n > 0
            assert len(people) > 0
            assert len(cars) > 0
            assert len(airports) > 0

            trips = []
            for i in range(n):
                person = random.choice(people)
                address = random.choice(addresses)
                job = random.choice(jobs)
                trips.append(
                    Transaction(f'T-{str(i).zfill(6)}', person.id, address.postcode, job.job, random.randint(100, 1000)))

            return trips

        people = generate_people(count_of_customers)
        addresses = generate_address(count_of_addresses)
        jobs = generate_job(count_of_jobs)
        transactions = generate_transactions(count_of_transactions, people, addresses, jobs)
        return RentalDataset(people, addresses, jobs, transactions)


@dataclass
class Transaction(Entity):
    id: str = field(hash=True)
    address: str = field(repr=True, compare=False)
    person: str = field(repr=True, compare=False)
    job: str = field(repr=True, compare=False)
    length: int = field(repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Transaction:
        return Transaction(seq[0], seq[1], seq[2], seq[3], int(seq[4]))

    def to_sequence(self) -> list[str]:
        return [self.id, self.address, self.person, self.job, str(self.length)]

    @staticmethod
    def field_names() -> list[str]:
        return ["id", "person", "address", "job", "length"]

    @staticmethod
    def collection_name() -> str:
        return "transactions"

    @staticmethod
    def create_table() -> str:
        return f"""
            CREATE TABLE {Transaction.collection_name()} (
                id VARCHAR(30) NOT NULL PRIMARY KEY,
                address CHAR(30) NOT NULL,
                person VARCHAR(40) NOT NULL,
                job VARCHAR(50) NOT NULL,
                length SMALLINT,

                FOREIGN KEY (airport) REFERENCES {Address.collection_name()}(code),
                FOREIGN KEY (person) REFERENCES {Person.collection_name()}(id),
                FOREIGN KEY (car) REFERENCES {Job.collection_name()}(plate)
            );
             """

@dataclass
class Address(Entity):
    postcode: str = field(hash=True)
    country: str = field(repr=True, compare=False)
    city: str = field(repr=True, compare=False)
    street_name: str = field(repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Address:
        return Address(seq[0], seq[1], seq[2], seq[3])

    def to_sequence(self) -> list[str]:
        return [self.postcode, self.country, self.city, self.street_name]

    @staticmethod
    def field_names() -> list[str]:
        return ["postcode", "country", "city", "street_name"]

    @staticmethod
    def collection_name() -> str:
        return "addresses"

    @staticmethod
    def create_table() -> str:
        return f"""
            CREATE TABLE {Address.collection_name()} (
                postcode CHAR(30) NOT NULL PRIMARY KEY,
                country VARCHAR(100),
                city VARCHAR(50),
                street_name VARCHAR(50),
            );
            """

@dataclass
class Person(Entity):
    id: str = field(hash=True)
    name: str = field(repr=True, compare=False)
    age: int = field(repr=True, compare=False)
    male: bool = field(default=True, repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Person:
        return Person(seq[0], seq[1], int(seq[2]), bool(seq[3]))

    def to_sequence(self) -> list[str]:
        return [self.id, self.name, str(self.age), str(int(self.male))]

    @staticmethod
    def field_names() -> list[str]:
        return ["id", "name", "age", "male"]

    @staticmethod
    def collection_name() -> str:
        return "people"

    @staticmethod
    def create_table() -> str:
        return f"""
            CREATE TABLE {Person.collection_name()} (
                id VARCHAR(8) NOT NULL PRIMARY KEY,
                name VARCHAR(50),
                age TINYINT,
                male BOOLEAN
            );
            """


@dataclass
class Job(Entity):
    job: str = field(hash=True)

    @staticmethod
    def from_sequence(seq: list[str]) -> Job:
        return Job(seq[0])

    def to_sequence(self) -> list[str]:
        return [self.job]

    @staticmethod
    def field_names() -> list[str]:
        return ["job"]

    @staticmethod
    def collection_name() -> str:
        return "jobs"

    @staticmethod
    def create_table() -> str:
        return f"""
            CREATE TABLE {Job.collection_name()} (
                job VARCHAR(50) NOT NULL PRIMARY KEY, 
            );
            """




