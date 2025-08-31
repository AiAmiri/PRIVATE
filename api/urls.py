from django.urls import path
from . import views
from .views import (
    sendhawalaAV, 
    FilteredsendhawalaAV,
    SarafProfileCreateView,
    SarafProfileDetailView,
    SarafProfileListView,
    SarafProfileLoginView,
    SarafProfileDualLoginView,
    CurrencyListView,
    CurrencyDetailView,
    ProvincesListView,
    ProvinceDetailView,
    SarafSupportedCurrenciesView,
    SarafProfilePhotoUpdateView,
    SarafLogoUpdateView,
    SarafLogoWallpaperUpdateView,
    LicencePhotoUpdateView,
    NormalUserProfileCreateView,
    NormalUserProfileLoginView,
    NormalUserProfileDetailView,
    NormalUserProfileListView,
    NormalUserProfilePhotoUpdateView,
    NormalUserLogoUpdateView,
    NormalUserWallpaperUpdateView,
    ReceiveHawalaCreateView, ReceiveHawalaDetailView, ReceiveHawalaListView, ReceiveHawalaVerifyView,
    normal_user_change_password, LogoutView, change_password,
    CustomerAccountCreateView, CustomerAccountListView, CustomerAccountDetailView,
    CustomerAccountDepositView, CustomerAccountWithdrawView, CustomerAccountTransactionsView,
    MessageSendView, MessageListView, MessageMarkReadView, ConversationListView,
    SarafColleagueListView, SarafColleagueCreateView, SarafColleagueDetailView,
    SarafLoanListView, SarafLoanCreateView, SarafLoanDetailView, SarafLoanRepayView, SarafLoanDefaultView,
    SarafPostCreateView,
)

urlpatterns = [
    # Sendhawala endpoints
    path('sendhawala/', sendhawalaAV.as_view(), name='send-hawala-api'),
    path('send-hawala/filter/', FilteredsendhawalaAV.as_view(), name='send-hawala-filter'),
    
    # SarafProfile endpoints
    path('saraf-profile/create/', SarafProfileCreateView.as_view(), name='saraf-profile-create'),
    path('saraf-profile/login/', SarafProfileLoginView.as_view(), name='saraf-profile-login'),
    path('saraf-profile/dual-login/', SarafProfileDualLoginView.as_view(), name='saraf-profile-dual-login'),
    path('saraf-profile/list/', SarafProfileListView.as_view(), name='saraf-profile-list'),
    path('saraf-profile/<int:saraf_id>/', SarafProfileDetailView.as_view(), name='saraf-profile-detail'),
    path('saraf-profile/<int:saraf_id>/supported-currencies/', SarafSupportedCurrenciesView.as_view(), name='saraf-supported-currencies'),
    path('saraf-profile/<int:saraf_id>/change-password/', change_password, name='saraf-profile-change-password'),
    path('saraf-profile/<int:saraf_id>/update-photos/', SarafProfilePhotoUpdateView.as_view(), name='saraf-profile-update-photos'),
    path('saraf-profile/<int:saraf_id>/update-saraf-logo/', SarafLogoUpdateView.as_view(), name='saraf-logo-update'),
    path('saraf-profile/<int:saraf_id>/update-saraf-logo-wallpeper/', SarafLogoWallpaperUpdateView.as_view(), name='saraf-logo-wallpeper-update'),
    path('saraf-profile/<int:saraf_id>/update-licence-photo/', LicencePhotoUpdateView.as_view(), name='licence-photo-update'),
    
    # Normal User Profile endpoints
    path('normal-user-profile/create/', NormalUserProfileCreateView.as_view(), name='normal-user-profile-create'),
    path('normal-user-profile/login/', NormalUserProfileLoginView.as_view(), name='normal-user-profile-login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('normal-user-profile/list/', NormalUserProfileListView.as_view(), name='normal-user-profile-list'),
    path('normal-user-profile/<int:normal_user_id>/', NormalUserProfileDetailView.as_view(), name='normal-user-profile-detail'),
    path('normal-user-profile/<int:normal_user_id>/change-password/', normal_user_change_password, name='normal-user-profile-change-password'),
    path('normal-user-profile/<int:normal_user_id>/update-photos/', NormalUserProfilePhotoUpdateView.as_view(), name='normal-user-profile-update-photos'),
    path('normal-user-profile/<int:normal_user_id>/update-user-logo/', NormalUserLogoUpdateView.as_view(), name='normal-user-logo-update'),
    path('normal-user-profile/<int:normal_user_id>/update-user-wallpaper/', NormalUserWallpaperUpdateView.as_view(), name='normal-user-wallpaper-update'),

    # Currency endpoints
    path('currencies/', CurrencyListView.as_view(), name='currency-list'),
    path('currencies/<int:currency_id>/', CurrencyDetailView.as_view(), name='currency-detail'),

    # Provinces
    path('provinces/', ProvincesListView.as_view(), name='province-list'),
    path('provinces/<str:province_name>/', ProvinceDetailView.as_view(), name='province-detail'),
    
    # ReceiveHawala endpoints
    path('receive-hawala/create/', ReceiveHawalaCreateView.as_view(), name='receive-hawala-create'),
    path('receive-hawala/list/', ReceiveHawalaListView.as_view(), name='receive-hawala-list'),
    path('receive-hawala/<int:pk>/', ReceiveHawalaDetailView.as_view(), name='receive-hawala-detail'),
    path('receive-hawala/<int:pk>/verify/', ReceiveHawalaVerifyView.as_view(), name='receive-hawala-verify'),
    
    # CustomerAccount endpoints
    path('customer-account/create/', CustomerAccountCreateView.as_view(), name='customer-account-create'),
    path('customer-account/list/', CustomerAccountListView.as_view(), name='customer-account-list'),
    path('customer-account/<int:account_id>/', CustomerAccountDetailView.as_view(), name='customer-account-detail'),
    path('customer-account/<int:account_id>/deposit/', CustomerAccountDepositView.as_view(), name='customer-account-deposit'),
    path('customer-account/<int:account_id>/withdraw/', CustomerAccountWithdrawView.as_view(), name='customer-account-withdraw'),
    path('customer-account/<int:account_id>/transactions/', CustomerAccountTransactionsView.as_view(), name='customer-account-transactions'),
    
    # Messaging endpoints
    path('messages/send/', MessageSendView.as_view(), name='message-send'),
    path('messages/list/', MessageListView.as_view(), name='message-list'),
    path('messages/<int:message_id>/mark-read/', MessageMarkReadView.as_view(), name='message-mark-read'),
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),

    # Saraf Posts
    path('saraf-posts/create/', SarafPostCreateView.as_view(), name='saraf-post-create'),
    
    # Colleague Management URLs
    path('colleagues/', views.SarafColleagueListView.as_view(), name='colleague-list'),
    path('colleagues/add/', views.SarafColleagueCreateView.as_view(), name='colleague-add'),
    path('colleagues/<int:colleague_id>/', views.SarafColleagueDetailView.as_view(), name='colleague-detail'),
    
    # Loan Management URLs
    path('loans/', views.SarafLoanListView.as_view(), name='loan-list'),
    path('loans/create/', views.SarafLoanCreateView.as_view(), name='loan-create'),
    path('loans/<int:loan_id>/', views.SarafLoanDetailView.as_view(), name='loan-detail'),
    
    # Currency Exchange URLs
    path('exchanges/', views.CurrencyExchangeListView.as_view(), name='exchange-list'),
    path('exchanges/create/', views.CurrencyExchangeCreateView.as_view(), name='exchange-create'),
    path('exchanges/<int:exchange_id>/', views.CurrencyExchangeDetailView.as_view(), name='exchange-detail'),
]
