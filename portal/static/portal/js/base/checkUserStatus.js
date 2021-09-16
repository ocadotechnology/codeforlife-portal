// Set to 'TEACHER', 'SCHOOL_STUDENT', 'INDEPENDENT_STUDENT', or 'UNTRACKED'
USER_STATUS = '{{ user|get_user_status }}';
DEVELOPER = '{{ user|is_developer }}' === 'True';
BETA = '{{ request|has_beta_access }}' === 'True';
