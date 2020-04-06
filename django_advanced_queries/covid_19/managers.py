from django.db.models import Manager, IntegerField, Max, Count, Avg, F, Case, When


class HospitalManager(Manager):
    def annotate_by_num_of_hospital_workers_in_risk_of_corona(self):
        return self.annotate(
            num_of_hospital_workers_in_risk_of_corona=Count(
                Case(
                    When(departments__hospital_workers__person__age__gte=60, then=1),
                    output_field=IntegerField
                ),
                distinct=True
            )
        )


class DepartmentManager(Manager):
    def annotate_avg_age_of_patients(self):
        return self.annotate(avg_age_of_patients=Avg('patients_details__person__age'))


class HospitalWorkerManager(Manager):
    def get_worker_performed_most_medical_examinations(self, filter_kwargs, exclude_kwargs):
        return self.filter(**filter_kwargs).exclude(**exclude_kwargs).annotate(
            num_pref_exams=Count('medical_examination_results')
        ).order_by('-num_pref_exams').first()

    def get_sick_workers(self):
        return self.annotate(
            latest_exam=Max('person__patients_details__medical_examination_results__time')
        ).filter(
            person__patients_details__medical_examination_results__time=F('latest_exam'),
            person__patients_details__medical_examination_results__result__in=['Corona', 'Botism']
        )


class PatientManager(Manager):
    def filter_by_examination_results(self, results, *args, **kwargs):
        return self.filter(medical_examination_results__result__in=results).filter(*args).filter(**kwargs)

    def get_highest_num_of_patient_medical_examinations(self):
        return self.annotate(
            num_of_patient_medical_examinations=Count('medical_examination_results')
            ).aggregate(
                highest_num_of_patient_medical_examinations=Max('num_of_patient_medical_examinations')
            )['highest_num_of_patient_medical_examinations']

    def filter_by_examined_hospital_workers(self, hospital_workers):
        return self.filter(
            medical_examination_results__time__in=hospital_workers.values_list('medical_examination_results__time')
        ).distinct()

class PersonManager(Manager):
    def get_sick_persons(self):
        return self.annotate(
            latest_exam=Max('patients_details__medical_examination_results__time')
        ).filter(
            patients_details__medical_examination_results__time=F('latest_exam'),
            patients_details__medical_examination_results__result__in=['Corona', 'Botism']
        )