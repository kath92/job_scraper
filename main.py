import datetime

from linkedin_api import Linkedin
import os
import sys
import mysql.connector
from mysql.connector import Error

LINKED_IN_PASSWORD = "" # fill out accordingly or store in environmental variable locally
LINKED_IN_USERNAME = "" # fill out accordingly

SEARCH_PHRASES = [
    "Data Analyst",
    "Data Specialist",
    "Power BI",
    "BI",
    "Tableau",
    "Business Intelligence"
]
SEARCH_LOCATION = "France"
MYSQL_CREDENTIALS = {
    "host": "localhost",
    "database": "linked_in_spider",
    "user": "", # fill out accordingly
    "password": "" # fill out accordingly
}
EXPERIENCES = {
    "1": "Internship",
    "2": "Junior",
    "3": "Associate",
    "4": "Senior",
    "5": "Director",
    "6": "Executive"
}


def main():
    try:
        for phrase in SEARCH_PHRASES:
            for experience in EXPERIENCES:
                fetch_for_phrase_and_experience(phrase, experience)
    except Exception as e:
        print(f"Error: {e}")


def fetch_for_phrase_and_experience(phrase, experience):
    username = os.getenv("LINKED_IN_USERNAME", LINKED_IN_USERNAME)
    password = os.getenv("LINKED_IN_PASSWORD", LINKED_IN_PASSWORD)
    print("Logging in...")
    api = Linkedin(username, password)
    print(f"Fetching job headers for phrase: '{phrase}' with experience: '{EXPERIENCES[experience]}'...")
    for job_header in api.search_jobs(keywords=phrase, experience=experience, location=SEARCH_LOCATION):
        job_id = job_header["trackingUrn"].replace("urn:li:jobPosting:", "")
        if job_exists(job_id):
            print(f"Job with id: {job_id} already exists in the database")
            try_insert_job_seniority_if_it_doesnt_exists(job_id, experience)
            continue
        print(f"Fetching job with id: {job_id}...")
        job = api.get_job(job_id)
        if ("companyDetails" not in job
                or "com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany" not in job[
                    "companyDetails"]):
            print("Skipping job due to missing company details")
            continue
        insert_job([
            job["jobPostingId"],
            job["companyDetails"]["com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany"][
                "companyResolutionResult"]["name"],
            job["title"],
            job["description"]["text"],
            datetime.datetime.fromtimestamp(job["listedAt"] / 1000.0).strftime('%Y-%m-%d'),
            None,
            extract_job_type(job),
            job["formattedLocation"]

        ])
        try_insert_job_seniority_if_it_doesnt_exists(job_id, experience)
        insert_job_skills(job)


def insert_job(job):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**MYSQL_CREDENTIALS)
        if connection.is_connected():
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO job (id, company_name, job_title, description, date, salary, job_type, location)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, job)
            connection.commit()
            print("Job inserted successfully")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def insert_job_skills(job):
    skills = get_skills()
    for skill in skills:
        if skill_exists_in_description(job["description"]["text"], skill[1]):
            try_insert_job_skill_if_it_doesnt_exists(job["jobPostingId"], skill[0])


def extract_job_type(job):
    if not "workplaceTypes" in job:
        return "Unknown"
    if "urn:li:fs_workplaceType:3" in job["workplaceTypes"]:
        return "Hybrid"
    if "urn:li:fs_workplaceType:1" in job["workplaceTypes"]:
        return "OnSite"
    if "urn:li:fs_workplaceType:2" in job["workplaceTypes"]:
        return "Remote"
    return "Unknown"


def job_exists(job_id):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**MYSQL_CREDENTIALS)
        if connection.is_connected():
            cursor = connection.cursor()
            select_query = """
            SELECT * FROM job WHERE id = %s
            """
            cursor.execute(select_query, (job_id,))
            return cursor.fetchone() is not None
    except Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def try_insert_job_seniority_if_it_doesnt_exists(job_id, experience):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**MYSQL_CREDENTIALS)
        if connection.is_connected():
            cursor = connection.cursor()
            select_query = """
            SELECT * FROM job_seniority WHERE job_id = %s AND name = %s
            """
            cursor.execute(select_query, (job_id, EXPERIENCES[experience]))
            if cursor.fetchone() is None:
                insert_query = """
                INSERT INTO job_seniority (job_id, name)
                VALUES (%s, %s)
                """
                cursor.execute(insert_query, (job_id, EXPERIENCES[experience]))
                connection.commit()
                print("Job seniority inserted successfully")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def get_skills():
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**MYSQL_CREDENTIALS)
        if connection.is_connected():
            cursor = connection.cursor()
            select_query = """
            SELECT * FROM skill
            """
            cursor.execute(select_query)
            return cursor.fetchall()
        raise Exception("Could not fetch skills")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def try_insert_job_skill_if_it_doesnt_exists(job_id, skill_id):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**MYSQL_CREDENTIALS)
        if connection.is_connected():
            cursor = connection.cursor()
            select_query = """
            SELECT * FROM job_skill WHERE job_id = %s AND skill_id = %s
            """
            cursor.execute(select_query, (job_id, skill_id))
            if cursor.fetchone() is None:
                insert_query = """
                INSERT INTO job_skill (job_id, skill_id)
                VALUES (%s, %s)
                """
                cursor.execute(insert_query, (job_id, skill_id))
                connection.commit()
                print("Job skill inserted successfully")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def skill_exists_in_description(job_description, skill):
    return skill.lower() in job_description.lower()


if __name__ == "__main__":
    sys.exit(main())
