"""
存储后端抽象层
支持: 本地存储、WebDAV、S3、SMB
"""
import os
from abc import ABC, abstractmethod

from django.conf import settings


class BaseStorageBackend(ABC):
    """存储后端基类"""

    @abstractmethod
    def upload(self, local_path, remote_path):
        """上传文件到远程存储"""
        ...

    @abstractmethod
    def download(self, remote_path, local_path):
        """从远程存储下载文件"""
        ...

    @abstractmethod
    def exists(self, path):
        """检查远程路径是否存在"""
        ...

    @abstractmethod
    def delete(self, path):
        """删除远程路径"""
        ...

    @abstractmethod
    def list_files(self, prefix=""):
        """列出远程文件"""
        ...


class LocalStorageBackend(BaseStorageBackend):
    """本地存储后端（兜底）"""

    def __init__(self, base_path=None):
        self.base_path = base_path or settings.MEDIA_ROOT

    def upload(self, local_path, remote_path):
        dest = os.path.join(self.base_path, remote_path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        import shutil
        shutil.copy2(local_path, dest)
        return dest

    def download(self, remote_path, local_path):
        src = os.path.join(self.base_path, remote_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        import shutil
        shutil.copy2(src, local_path)
        return local_path

    def exists(self, path):
        return os.path.exists(os.path.join(self.base_path, path))

    def delete(self, path):
        full_path = os.path.join(self.base_path, path)
        if os.path.exists(full_path):
            os.remove(full_path)

    def list_files(self, prefix=""):
        result = []
        base = os.path.join(self.base_path, prefix)
        if os.path.exists(base):
            for root, dirs, files in os.walk(base):
                for f in files:
                    rel = os.path.relpath(os.path.join(root, f), self.base_path)
                    result.append(rel)
        return result


class WebDAVStorageBackend(BaseStorageBackend):
    """WebDAV 存储后端"""

    def __init__(self, url, username="", password=""):
        self.url = url.rstrip("/")
        self.username = username
        self.password = password

    def _connect(self):
        try:
            import webdav3.client as wc
            options = {
                "webdav_hostname": self.url,
                "webdav_login": self.username,
                "webdav_password": self.password,
            }
            return wc.Client(options)
        except ImportError:
            raise ImportError("请安装 webdavclient3: pip install webdavclient3")

    def upload(self, local_path, remote_path):
        client = self._connect()
        client.upload_file(remote_path, local_path)
        return remote_path

    def download(self, remote_path, local_path):
        client = self._connect()
        client.download_file(remote_path, local_path)
        return local_path

    def exists(self, path):
        client = self._connect()
        return client.check(path)

    def delete(self, path):
        client = self._connect()
        client.clean(path)

    def list_files(self, prefix=""):
        client = self._connect()
        return client.list(prefix)


class S3StorageBackend(BaseStorageBackend):
    """S3 兼容对象存储后端"""

    def __init__(self, bucket, access_key, secret_key, endpoint=None, region="us-east-1"):
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint = endpoint
        self.region = region

    def _get_client(self):
        import boto3
        kwargs = {
            "aws_access_key_id": self.access_key,
            "aws_secret_access_key": self.secret_key,
            "region_name": self.region,
        }
        if self.endpoint:
            kwargs["endpoint_url"] = self.endpoint
        return boto3.client("s3", **kwargs)

    def upload(self, local_path, remote_path):
        client = self._get_client()
        client.upload_file(local_path, self.bucket, remote_path)
        return remote_path

    def download(self, remote_path, local_path):
        client = self._get_client()
        client.download_file(self.bucket, remote_path, local_path)
        return local_path

    def exists(self, path):
        client = self._get_client()
        try:
            client.head_object(Bucket=self.bucket, Key=path)
            return True
        except Exception:
            return False

    def delete(self, path):
        client = self._get_client()
        client.delete_object(Bucket=self.bucket, Key=path)

    def list_files(self, prefix=""):
        client = self._get_client()
        response = client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        return [obj["Key"] for obj in response.get("Contents", [])]


class SMBStorageBackend(BaseStorageBackend):
    """SMB 共享存储后端"""

    def __init__(self, host, share, username="", password="", domain=""):
        self.host = host
        self.share = share
        self.username = username
        self.password = password
        self.domain = domain

    def _connect(self):
        try:
            from smb.SMBConnection import SMBConnection
            conn = SMBConnection(
                self.username,
                self.password,
                "assignment_system",
                self.host,
                domain=self.domain,
                use_ntlm_v2=True,
            )
            conn.connect(self.host, 445)
            return conn
        except ImportError:
            raise ImportError("请安装 pysmb: pip install pysmb")

    def upload(self, local_path, remote_path):
        conn = self._connect()
        with open(local_path, "rb") as f:
            conn.storeFile(self.share, remote_path, f)
        conn.close()
        return remote_path

    def download(self, remote_path, local_path):
        conn = self._connect()
        with open(local_path, "wb") as f:
            conn.retrieveFile(self.share, remote_path, f)
        conn.close()
        return local_path

    def exists(self, path):
        conn = self._connect()
        try:
            conn.getAttributes(self.share, path)
            conn.close()
            return True
        except Exception:
            conn.close()
            return False

    def delete(self, path):
        conn = self._connect()
        conn.deleteFiles(self.share, path)
        conn.close()

    def list_files(self, prefix=""):
        conn = self._connect()
        files = conn.listPath(self.share, prefix)
        conn.close()
        return [f.filename for f in files if f.filename not in (".", "..")]


def get_storage_backend(backend_type="local", settings_obj=None):
    """根据后端类型和设置返回对应的存储后端实例"""
    if settings_obj is None:
        from assignments.models import LiveSettings
        settings_obj = LiveSettings.load()

    if backend_type == "webdav":
        return WebDAVStorageBackend(
            url=settings_obj.webdav_url,
            username=settings_obj.webdav_username,
            password=settings_obj.webdav_password,
        )
    elif backend_type == "s3":
        return S3StorageBackend(
            bucket=settings_obj.s3_bucket,
            access_key=settings_obj.s3_access_key,
            secret_key=settings_obj.s3_secret_key,
            endpoint=settings_obj.s3_endpoint,
            region=settings_obj.s3_region,
        )
    elif backend_type == "smb":
        return SMBStorageBackend(
            host=settings_obj.smb_host,
            share=settings_obj.smb_share,
            username=settings_obj.smb_username,
            password=settings_obj.smb_password,
            domain=settings_obj.smb_domain,
        )
    else:
        return LocalStorageBackend()