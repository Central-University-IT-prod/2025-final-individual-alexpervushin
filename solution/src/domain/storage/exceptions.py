class MinioServiceError(Exception):

    pass


class MinioUploadError(MinioServiceError):

    pass


class MinioDeleteError(MinioServiceError):

    pass


class MinioGetUrlError(MinioServiceError):

    pass


class MinioInvalidFileType(MinioServiceError):

    pass
