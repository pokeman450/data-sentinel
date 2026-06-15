def health_check():
    return {
        "status": "ok",
        "service": "data-sentinel",
        "checks": {
            "api": True,
            "version": "0.1.0"
        }
    }