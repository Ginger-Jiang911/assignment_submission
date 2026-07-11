"""
Django 管理命令：自动备份到远程存储和本地清理
"""
import logging
import os
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from assignments.models import LiveSettings, Project, Submission
from storage_backends import get_storage_backend

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "自动备份本地文件到远程存储并可选清理本地存档"

    def handle(self, *args, **options):
        s = LiveSettings.load()

        if not s.backup_enabled:
            self.stdout.write("自动备份未启用，跳过。")
            return

        self.stdout.write("=" * 60)
        self.stdout.write(f"备份任务开始 — {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write("=" * 60)

        try:
            # 对每个使用非本地存储的项目执行备份
            remote_projects = Project.objects.exclude(storage_backend="local")
            if not remote_projects.exists():
                self.stdout.write("没有配置远程存储的项目，跳过。")
                return

            local_storage = get_storage_backend("local")
            all_success = True

            for project in remote_projects:
                remote_storage = get_storage_backend(project.storage_backend, s)
                submissions = Submission.objects.filter(project=project)

                self.stdout.write(f"\n📁 备份项目: {project.name} ({project.storage_backend})")

                for sub in submissions:
                    if sub.file:
                        local_path = os.path.join(settings.MEDIA_ROOT, sub.file.name)
                        if os.path.exists(local_path):
                            try:
                                remote_storage.upload(local_path, sub.file.name)
                                self.stdout.write(f"  ✅ {sub.file.name}")
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f"  ❌ {sub.file.name}: {e}"))
                                all_success = False
                        else:
                            self.stdout.write(self.style.WARNING(f"  ⚠️ 本地文件不存在: {sub.file.name}"))

            self.stdout.write(f"\n备份结果: {'✅ 全部成功' if all_success else '❌ 部分失败'}")

            # 如果备份成功，尝试自动清理
            if all_success and s.auto_cleanup_enabled:
                self._cleanup_local_files(s)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"备份任务失败: {e}"))

    def _cleanup_local_files(self, settings_obj):
        """清理过期的本地文件"""
        days = settings_obj.cleanup_after_backup
        self.stdout.write(f"\n🗑️ 开始清理本地存档 (策略: {days}天后清理)")

        if days == 0:
            # 立即清理所有
            self._delete_all_local()
        else:
            # 清理 days 天前的文件
            cutoff = timezone.now() - timedelta(days=days)
            old_submissions = Submission.objects.filter(submitted_at__lt=cutoff)
            count = 0
            for sub in old_submissions:
                if sub.file:
                    local_path = os.path.join(settings.MEDIA_ROOT, sub.file.name)
                    if os.path.exists(local_path):
                        try:
                            os.remove(local_path)
                            count += 1
                            self.stdout.write(f"  🗑️ {sub.file.name}")
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"  ❌ {sub.file.name}: {e}"))
            self.stdout.write(f"清理完成，共删除 {count} 个文件。")

    def _delete_all_local(self):
        """删除所有本地文件"""
        import shutil
        media_root = settings.MEDIA_ROOT
        if os.path.exists(media_root):
            for item in os.listdir(media_root):
                item_path = os.path.join(media_root, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ❌ 删除失败: {item_path}: {e}"))
            self.stdout.write("本地存档已全部清理。")