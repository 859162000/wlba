diff --git a/marketing/models.py b/marketing/models.py
index 9813f8e..b1372f3 100644
--- a/marketing/models.py
+++ b/marketing/models.py
@@ -149,3 +149,17 @@ class Activity(models.Model):
 
     def __unicode__(self):
         return u'<%s>' % self.name
+
+
+class Reward(models.Model):
+    """ 奖品存储
+    """
+    pass
+
+
+class RewardRecord(models.Model):
+    """ 奖品发放流水
+    """
+    pass
+
+
diff --git a/wanglibao_margin/admin.py b/wanglibao_margin/admin.py
index 43ce97a..6e325c1 100644
--- a/wanglibao_margin/admin.py
+++ b/wanglibao_margin/admin.py
@@ -10,6 +10,7 @@ class UserMarginAdmin(admin.ModelAdmin):
 class MarginRecordAdmin(admin.ModelAdmin):
     list_display = ('catalog', 'user', 'amount', 'description', 'margin_current')
     search_fields = ('user__wanglibaouserprofile__phone',)
+    raw_id_fields = ('user', )
 
 admin.site.register(Margin, UserMarginAdmin)
 admin.site.register(MarginRecord, MarginRecordAdmin)
\ No newline at end of file
diff --git a/wanglibao_margin/models.py b/wanglibao_margin/models.py
index 8da07f3..054d919 100644
--- a/wanglibao_margin/models.py
+++ b/wanglibao_margin/models.py
@@ -1,7 +1,6 @@
 # encoding: utf-8
 from decimal import Decimal
 from django.db import models
-#from django.contrib.auth import get_user_model
 from django.contrib.auth.models import User
 from django.db.models.signals import post_save
 from django.contrib.auth.models import User
