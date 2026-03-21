from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import UniqueConstraint

class User(AbstractUser):
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=14, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.email}"

# Carteira de investimentos do usuário, pode ter vários assets(açoes, fundos, etc)
class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="portfolios") # cascade pois se deletar o usuário, tb deleta os portfólios dele
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
class Asset(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="assets")
    ticker = models.CharField(max_length=10)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Dados da BRAPI (sincronizados no cadastro)
    company_name = models.CharField(max_length=200, blank=True, null=True)  # ex: Petrobras
    sector = models.CharField(max_length=100, blank=True, null=True)  # ex: Energia
    current_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)  # preço atual
    price_change_percent = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)  # variação %
    market_cap = models.CharField(max_length=50, blank=True, null=True)  # valor de mercado (ex: "2.5B")
    dividend_yield = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)  # rendimento %

    class Meta:
        constraints = [
            UniqueConstraint(fields=['portfolio', 'ticker'], name='unique_portfolio_ticker')
        ]

    def __str__(self):
        return f"{self.ticker} ({self.company_name}) - {self.quantity} @ {self.purchase_price} ({self.portfolio.name})"