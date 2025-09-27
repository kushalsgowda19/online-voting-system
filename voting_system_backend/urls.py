from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home_view(_request):
    return HttpResponse(
        """
        <html>
          <head><title>Online Voting System</title></head>
          <body style="font-family:system-ui,Segoe UI,Arial;margin:40px;">
            <h1>Online Voting System</h1>
            <p>Your backend is running.</p>
            <ul>
              <li><a href="/admin/">Admin</a></li>
              <li><a href="/api/">API root (accounts/elections)</a></li>
              <li>Register: <code>POST /api/register/</code></li>
              <li>Token: <code>POST /api/token/</code></li>
              <li>Elections: <code>GET /api/elections/</code></li>
              <li>Results: <code>GET /api/results/&lt;election_id&gt;/</code></li>
            </ul>
          </body>
        </html>
        """,
        content_type="text/html",
    )


urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('elections.urls')),
]
