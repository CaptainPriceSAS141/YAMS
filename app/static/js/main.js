/**
 * Main JavaScript file for Stock Market Trend Analysis
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Search form functionality
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = document.getElementById('searchInput');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                alert('Please enter a search term');
            }
        });
    }

    // Stock comparison form
    const compareForm = document.getElementById('compareForm');
    if (compareForm) {
        compareForm.addEventListener('submit', function(e) {
            const symbolsInput = document.getElementById('symbolsInput');
            if (!symbolsInput.value.trim()) {
                e.preventDefault();
                alert('Please enter at least one stock symbol');
            }
        });
    }

    // Watchlist delete confirmation
    const deleteButtons = document.querySelectorAll('.delete-watchlist-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this watchlist?')) {
                e.preventDefault();
            }
        });
    });

    // Stock removal confirmation
    const removeStockButtons = document.querySelectorAll('.remove-stock-btn');
    removeStockButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to remove this stock from your watchlist?')) {
                e.preventDefault();
            }
        });
    });

    // Password confirmation check
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');
            
            if (password.value !== confirmPassword.value) {
                e.preventDefault();
                alert('Passwords do not match');
            }
        });
    }

    // Auto-update stock prices (every 60 seconds)
    const stockPrices = document.querySelectorAll('.stock-price');
    if (stockPrices.length > 0) {
        setInterval(updateStockPrices, 60000);
    }

    // Function to update stock prices via AJAX
    function updateStockPrices() {
        stockPrices.forEach(priceElement => {
            const symbol = priceElement.dataset.symbol;
            if (symbol) {
                fetch(`/api/stock/${symbol}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success && data.data.length > 0) {
                            const latestData = data.data[data.data.length - 1];
                            const price = latestData.Close;
                            const previousPrice = parseFloat(priceElement.dataset.previousPrice || 0);
                            
                            // Update price
                            priceElement.textContent = `$${price.toFixed(2)}`;
                            priceElement.dataset.previousPrice = price;
                            
                            // Update color based on price change
                            if (price > previousPrice) {
                                priceElement.classList.remove('price-down', 'price-neutral');
                                priceElement.classList.add('price-up');
                            } else if (price < previousPrice) {
                                priceElement.classList.remove('price-up', 'price-neutral');
                                priceElement.classList.add('price-down');
                            } else {
                                priceElement.classList.remove('price-up', 'price-down');
                                priceElement.classList.add('price-neutral');
                            }
                        }
                    })
                    .catch(error => console.error('Error updating stock price:', error));
            }
        });
    }

    // Chart period selector
    const periodButtons = document.querySelectorAll('.period-btn');
    periodButtons.forEach(button => {
        button.addEventListener('click', function() {
            periodButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const period = this.dataset.period;
            const symbol = this.dataset.symbol;
            
            if (symbol && period) {
                updateCharts(symbol, period);
            }
        });
    });

    // Function to update charts based on period
    function updateCharts(symbol, period) {
        fetch(`/api/stock/${symbol}?period=${period}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update charts with new data
                    // This would depend on your charting library
                    console.log('Chart data updated for period:', period);
                }
            })
            .catch(error => console.error('Error updating charts:', error));
    }
}); 