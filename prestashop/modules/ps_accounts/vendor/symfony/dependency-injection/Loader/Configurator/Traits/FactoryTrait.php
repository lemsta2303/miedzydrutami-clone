<?php

/*
 * This file is part of the Symfony package.
 *
 * (c) Fabien Potencier <fabien@symfony.com>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */
namespace PrestaShop\Module\PsAccounts\Vendor\Symfony\Component\DependencyInjection\Loader\Configurator\Traits;

use PrestaShop\Module\PsAccounts\Vendor\Symfony\Component\DependencyInjection\Exception\InvalidArgumentException;
trait FactoryTrait
{
    /**
     * Sets a factory.
     *
     * @param string|array $factory A PHP callable reference
     *
     * @return $this
     */
    public final function factory($factory)
    {
        if (\is_string($factory) && 1 === \substr_count($factory, ':')) {
            $factoryParts = \explode(':', $factory);
            throw new InvalidArgumentException(\sprintf('Invalid factory "%s": the `service:method` notation is not available when using PHP-based DI configuration. Use "[ref(\'%s\'), \'%s\']" instead.', $factory, $factoryParts[0], $factoryParts[1]));
        }
        $this->definition->setFactory(static::processValue($factory, \true));
        return $this;
    }
}
